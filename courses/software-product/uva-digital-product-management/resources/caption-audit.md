# UVA 字幕与逐字文本进一步核查

核对日期：2026-10-03。使用 video-subtitle-transcript 技能，遵循仓库时间戳规范；仅检查公开网页及字幕列表，不登录、不用 cookies、不下载音视频。

## 五门当前 Coursera 子课程

五门公开课程页面均可以读取模块目录，但公开 HTML 中没有发现 lesson 链接或 VTT/SRT 地址。没有构造私有接口或推测 lesson ID。这不代表所有平台课时都没有字幕，只代表本轮无账户条件下没有获取入口。全部课程中英文完整逐字稿仍为 0。

## 独立补充的真实公开文本

教师官方站的 [Josh Andrews 访谈](https://www.alexandercowan.com/josh-andrews-product-manager-google/)确有完整英文说话人逐字文本，可在原站阅读。没有段落时间戳，未确认转载许可，因此登记 [独立来源说明](../references/public-transcript-sources/josh-andrews-source-reference.md)和全文外链，没有复制全文或编造时间轴。

## 公开 YouTube 字幕探测

教师 [产品管线页面](https://www.alexandercowan.com/your-delivery-pipeline/)嵌入 [Jez Humble 访谈](https://www.youtube.com/watch?v=6sE9ttHL-3M)。使用 yt-dlp 的 skip-download/list-subs 模式探测，返回“The page needs to be reloaded”，没有获取字幕列表或字幕文件。访谈不是 Coursera 当前课堂，不计作任何课程视频覆盖。未改用音频下载、登录态或外部字幕镜像。

## 另一平台的公开学习页面

找到 [FutureLearn Digital Product Management 公开步骤归档](https://www.futurelearn.com/info/step-course/digital-product-management)及 [Why is a product never a product?](https://www.futurelearn.com/info/courses/digital-product-management/0/steps/69959)。公开可读内容是学习摘要，没有取得完整时间轴字幕。该平台版本与当前 Coursera 版的映射未确认，不能用旧内容冒充最新版逐字稿。

机器可读记录见 [caption-audit.yaml](caption-audit.yaml)。这次补充增加真实文本来源入口，没有增加可发布或完整带时间戳逐字稿。
