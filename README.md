# Discord 實況直播通知機器人

一個使用 Python 開發的 Discord 機器人，提供 YouTube 實況開播查詢、追蹤連結管理與 Hololive 行程表查詢功能。透過 Selenium 進行網頁自動化，取得實況相關資訊，並在 Discord 中以指令回覆使用者，協助社群掌握實況動態。

## 核心功能

- **實況狀態查詢：** 使用 `STREAM` 指令查詢實況主的直播狀態，並回傳相關訊息。
- **追蹤連結管理：** 支援新增追蹤連結與查看追蹤列表，方便管理需要關注的實況頻道。
- **Hololive 行程表查詢：** 使用指令取得 Hololive 行程表相關資訊。
- **網頁自動化：** 使用 Selenium 擷取網頁資訊，減少手動查詢的需求。

## 功能展示

### 1. 實況狀態查詢

透過 `STREAM` 指令查詢實況狀態，並確認機器人能正確回傳相關訊息。

![STREAM 指令回傳實況狀態訊息](https://cdn.discordapp.com/attachments/1051148177769767045/1559234403945680996/2026-10-12_235929.png?ex=6ace55b3&is=6acd0433&hm=6c5237e0b666fc3340a9d0182e663010d314282159673ec4d9077ab6cf71ffc6&)

### 2. 追蹤連結管理

提供新增追蹤連結及查看追蹤列表的功能，讓使用者能管理想追蹤的實況頻道。

![新增追蹤連結及查看追蹤列表](https://cdn.discordapp.com/attachments/1051148177769767045/1559234404692529213/2026-10-12_235857.png?ex=6ace55b3&is=6acd0433&hm=d04214d4149b8b78b5896eb4c1bd1f14e95d3860b9a0b8e21c15e988832a4209&)

### 3. Hololive 行程表查詢

透過指令取得 Hololive 行程表的回傳內容，方便使用者查看相關行程資訊。

![Hololive 行程表指令回傳內容](https://cdn.discordapp.com/attachments/1051148177769767045/1559234405128609812/2026-10-12_235920.png?ex=6ace55b3&is=6acd0433&hm=bdb1d44fb7abd3701d04099af3e3a85e7e2facc0b2c552ecbf48074a21bbd4f9&)

## 使用技術

- **Python：** 機器人功能與指令處理
- **Discord Bot：** Discord 訊息互動與指令回覆
- **Selenium：** 網頁自動化與資訊擷取
- **Docker：** 打包執行環境
- **AWS / Azure：** 曾用於建立虛擬機並託管機器人

## 專案目的

透過實作 Discord 機器人，練習 Python 程式開發、網頁自動化、Discord 指令處理與程式部署，並將不同功能整合至同一個機器人中。
