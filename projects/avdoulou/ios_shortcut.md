# iOS 快捷指令 - X 视频下载

## 快捷指令配置

### 方式一：导入快捷指令（推荐）

1. 在 iPhone 上复制以下链接，在 Safari 中打开：
   ```
   https://www.icloud.com/shortcuts/[你的快捷指令ID]
   ```

### 方式二：手动创建

#### 步骤 1: 创建新快捷指令

1. 打开"快捷指令"App
2. 点击右上角 "+" 创建新快捷指令
3. 命名为 "X 视频下载"

#### 步骤 2: 添加操作

按顺序添加以下操作：

**1. 获取剪贴板内容**
- 操作：`从输入中获取`
- 或：`获取剪贴板`

**2. 检查是否为 X 链接**
- 操作：`如果`
- 条件：`输入` 包含 `x.com` 或 `twitter.com`

**3. 调用 API**
- 操作：`获取 URL 内容`
- URL: `http://你的服务器IP:8080/extract?url=剪贴板内容`
- 方法: `GET`
- 请求头: `Content-Type: application/json`

**4. 解析 JSON 响应**
- 操作：`获取字典值`
- 获取 `video.url` (视频) 或 `photos` (图片)

**5. 下载媒体**
- 操作：`下载 URL`
- 传入步骤 4 获取的 URL

**6. 保存到相册**
- 操作：`存储到相册`

#### 快捷指令 JSON (直接导入)

复制以下内容，在快捷指令 App 中导入：

```json
{
  "WFWorkflowActions": [
    {
      "WFWorkflowActionIdentifier": "WFGetClipboardContentAction",
      "WFWorkflowActionParameters": {}
    },
    {
      "WFWorkflowActionIdentifier": "WFConditionalAction",
      "WFWorkflowActionParameters": {
        "WFControlFlowMode": 0,
        "WFCondition": {
          "WFConditionActionCount": 1,
          "WFConditions": [
            {
              "WFConditionActionType": 0,
              "WFConditionComparison": 6,
              "WFConditionVariable": {
                "Value": {
                  "string": "x.com\ntwitter.com",
                  "attachmentsByRange": {}
                },
                "WFVariableType": "Value"
              },
              "WFConditionVariableValue": {
                "Value": {
                  "string": "◆剪贴板内容◆",
                  "attachmentsByRange": {}
                },
                "WFVariableType": "Variable"
              }
            }
          ]
        }
      }
    },
    {
      "WFWorkflowActionIdentifier": "WFHTTPRequestAction",
      "WFWorkflowActionParameters": {
        "WFHTTPMethod": "GET",
        "WFURL": "http://你的服务器IP:8080/extract?url=",
        "WFHeaders": {
          "Value": {
            "Content-Type": "application/json"
          }
        }
      }
    },
    {
      "WFWorkflowActionIdentifier": "WFGetDictionaryValueAction",
      "WFWorkflowActionParameters": {
        "WFDictionaryKey": "video"
      }
    },
    {
      "WFWorkflowActionIdentifier": "WFGetDictionaryValueAction",
      "WFWorkflowActionParameters": {
        "WFDictionaryKey": "url"
      }
    },
    {
      "WFWorkflowActionIdentifier": "WFDownloadURLAction",
      "WFWorkflowActionParameters": {}
    },
    {
      "WFWorkflowActionIdentifier": "WFSavePhotoAssetAction",
      "WFWorkflowActionParameters": {}
    }
  ],
  "WFWorkflowMinimumClientVersion": 900,
  "WFWorkflowMinimumClientVersionString": "900",
  "WFWorkflowTypes": ["NCWidget", "WatchKit"]
}
```

## 使用方法

### 本地运行（无需云服务器）

1. **在 Mac 上运行 API 服务**：
   ```bash
   cd /Users/duola/projects/avdoulou
   python3 server.py --host 0.0.0.0 --port 8080
   ```

2. **确保 Mac 和 iPhone 在同一 Wi-Fi**

3. **获取 Mac 的 IP 地址**：
   ```bash
   ipconfig getifaddr en0
   ```

4. **在快捷指令中更新 URL**：
   ```
   http://你的Mac_IP:8080/extract?url=
   ```

### 云服务器运行（推荐，随时可用）

1. **部署到云服务器**（阿里云、腾讯云等）
2. **使用 HTTPS**（快捷指令要求）
3. **更新快捷指令中的 URL**

## 简化版快捷指令（不需要服务器）

如果你不想运行服务器，可以使用这个简化版本：

1. **获取剪贴板**
2. **打开 URL**：直接在 Safari 中打开推文链接
3. **手动保存视频**

---

## 完整快捷指令示例

### "X 视频下载" 快捷指令

```
快捷指令名称: X 视频下载
图标: 选择 Twitter 或视频图标
颜色: 蓝色

操作流程:
┌─────────────────────────────────────┐
│ 1. 从输入获取 / 获取剪贴板          │
│    - 输入: 推文链接                 │
├─────────────────────────────────────┤
│ 2. 如果: 输入包含 "x.com"           │
├─────────────────────────────────────┤
│ 3. 获取 URL 内容                    │
│    - URL: http://192.168.x.x:8080   │
│           /extract?url=【剪贴板】   │
│    - 方法: GET                      │
├─────────────────────────────────────┤
│ 4. 获取字典值: video > url          │
├─────────────────────────────────────┤
│ 5. 下载 URL                         │
├─────────────────────────────────────┤
│ 6. 存储到相册                       │
├─────────────────────────────────────┤
│ 7. 显示通知: "视频已保存"           │
└─────────────────────────────────────┘
```
