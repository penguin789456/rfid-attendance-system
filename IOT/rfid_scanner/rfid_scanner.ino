/*
 * ============================================================
 *  RFID 出勤打卡器 — ESP32 + MFRC522
 * ============================================================
 *  讀取 RFID 卡片 UID，透過 WiFi 呼叫後端 POST /api/scan
 *
 *  硬體接線 (ESP32 ↔ MFRC522):
 *    SDA(SS) → GPIO 5
 *    SCK     → GPIO 18
 *    MOSI    → GPIO 23
 *    MISO    → GPIO 19
 *    RST     → GPIO 22
 *    3.3V    → 3.3V
 *    GND     → GND
 *
 *  所需函式庫:
 *    - MFRC522      (by miguelbalboa)
 *    - ArduinoJson  (by Benoit Blanchon)
 * ============================================================
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <SPI.h>
#include <MFRC522.h>
#include <ArduinoJson.h>
#include <time.h>

// ===================== 使用者設定區 =====================
// WiFi
const char* WIFI_SSID     = "pocof6";
const char* WIFI_PASSWORD  = "bin45177096";

// 後端伺服器
const char* SERVER_IP   = "10.85.187.98";   // 改為你的後端 IP
const int   SERVER_PORT = 8000;

// 裝置識別碼（可區分不同讀卡器）
const char* DEVICE_ID = "ESP32_READER_01";

// 時區（UTC+8 台灣）
const long  GMT_OFFSET_SEC   = 8 * 3600;   // +08:00
const int   DAYLIGHT_OFFSET  = 0;           // 台灣無日光節約
const char* NTP_SERVER       = "pool.ntp.org";
const char* TZ_OFFSET_STR   = "+08:00";    // ISO 8601 時區字串

// 防重複掃描間隔（毫秒）
const unsigned long DEBOUNCE_MS = 2000;
// ========================================================

// MFRC522 腳位
#define SS_PIN   5
#define RST_PIN  22

MFRC522 mfrc522(SS_PIN, RST_PIN);

// 防重複掃描用
String   lastUID     = "";
unsigned long lastScanTime = 0;

// -------------------- 初始化 --------------------
void setup() {
  Serial.begin(115200);
  Serial.println();
  Serial.println("========================================");
  Serial.println("  RFID 出勤打卡器 啟動中...");
  Serial.println("========================================");

  // ----- WiFi 連線 -----
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("連接 WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("WiFi 已連線, IP: ");
  Serial.println(WiFi.localIP());

  // ----- NTP 時間同步 -----
  configTime(GMT_OFFSET_SEC, DAYLIGHT_OFFSET, NTP_SERVER);
  Serial.print("NTP 時間同步中");
  struct tm timeinfo;
  while (!getLocalTime(&timeinfo)) {
    Serial.print(".");
    delay(500);
  }
  Serial.println();
  Serial.print("目前時間: ");
  Serial.println(&timeinfo, "%Y-%m-%d %H:%M:%S");

  // ----- SPI + MFRC522 -----
  SPI.begin();
  mfrc522.PCD_Init();
  delay(100);
  mfrc522.PCD_DumpVersionToSerial();
  Serial.println("MFRC522 就緒，請刷卡...");
  Serial.println("----------------------------------------");
}

// -------------------- 主迴圈 --------------------
void loop() {
  // 檢查 WiFi 連線
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[WARN] WiFi 斷線，嘗試重新連線...");
    WiFi.reconnect();
    delay(3000);
    return;
  }

  // 偵測卡片
  if (!mfrc522.PICC_IsNewCardPresent()) return;
  if (!mfrc522.PICC_ReadCardSerial())   return;

  // 讀取 UID → 十六進位字串（大寫，無分隔）
  String uid = getUIDString();
  Serial.print("偵測到卡片 UID: ");
  Serial.println(uid);

  // 防重複：同一張卡在 DEBOUNCE_MS 內不重複觸發
  unsigned long now = millis();
  if (uid == lastUID && (now - lastScanTime) < DEBOUNCE_MS) {
    Serial.println("  → 重複掃描，略過");
    haltCard();
    return;
  }
  lastUID      = uid;
  lastScanTime = now;

  // 呼叫後端 API
  callScanAPI(uid);

  // 結束與卡片的通訊
  haltCard();
}

// -------------------- 讀取 UID 字串 --------------------
String getUIDString() {
  String uid = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    if (mfrc522.uid.uidByte[i] < 0x10) {
      uid += "0";
    }
    uid += String(mfrc522.uid.uidByte[i], HEX);
  }
  uid.toUpperCase();
  return uid;
}

// -------------------- 停止與卡片通訊 --------------------
void haltCard() {
  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();
}

// -------------------- 取得 ISO 8601 時間字串（含時區） --------------------
// 輸出格式: "2025-02-11T14:35:00+08:00"
String getISO8601Time() {
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    return "";  // NTP 尚未同步
  }
  char buf[30];
  strftime(buf, sizeof(buf), "%Y-%m-%dT%H:%M:%S", &timeinfo);
  return String(buf) + TZ_OFFSET_STR;
}

// -------------------- 呼叫 Scan API --------------------
void callScanAPI(String rfidID) {
  HTTPClient http;

  // 組合 URL
  String url = "http://" + String(SERVER_IP) + ":" + String(SERVER_PORT) + "/api/scan";

  // 建立 JSON payload（含 timezone-aware event_time）
  JsonDocument doc;
  doc["rfid_id"]   = rfidID;
  doc["device_id"] = DEVICE_ID;
  String eventTime = getISO8601Time();
  if (eventTime.length() > 0) {
    doc["event_time"] = eventTime;
  }

  String payload;
  serializeJson(doc, payload);

  Serial.print("  → POST ");
  Serial.println(url);
  Serial.print("  → Body: ");
  Serial.println(payload);

  // 發送 HTTP POST
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  int httpCode = http.POST(payload);

  if (httpCode > 0) {
    String response = http.getString();
    Serial.print("  → HTTP ");
    Serial.println(httpCode);

    // 解析回應 JSON
    JsonDocument resDoc;
    DeserializationError err = deserializeJson(resDoc, response);

    if (!err) {
      bool   success      = resDoc["success"];
      const char* message  = resDoc["message"];
      const char* empName  = resDoc["employee_name"];
      const char* scanType = resDoc["scan_type"];

      Serial.println("  ┌──────────────────────────────");
      if (success) {
        Serial.print("  │ ✔ ");
        Serial.println(message);
        Serial.print("  │ 員工: ");
        Serial.println(empName ? empName : "N/A");
        Serial.print("  │ 類型: ");
        Serial.println(scanType ? scanType : "N/A");
        Serial.print("  │ 工作日: ");
        Serial.println(resDoc["work_date"].as<const char*>());
      } else {
        Serial.print("  │ ✘ ");
        Serial.println(message);
      }
      Serial.println("  └──────────────────────────────");
    } else {
      Serial.print("  → JSON 解析失敗: ");
      Serial.println(err.c_str());
      Serial.print("  → Raw: ");
      Serial.println(response);
    }
  } else {
    Serial.print("  → HTTP 錯誤: ");
    Serial.println(http.errorToString(httpCode));
  }

  http.end();
  Serial.println("----------------------------------------");
}
