/**
 * ==========================================
 * ★★★ EV1 播放器配置区域 ★★★
 * 对应 videoList.js 中的 EV1
 * ==========================================
 */
const config = {
    // 视频基本信息
    title: "面包",
    id: "EV1",
    date: "2025-02-27",
    author: "Ellari",
    
    // 视频文件路径
    videoSrc: "/vid/Bread_Low.mp4",
    
    // 视频封面图 (可选, 留空则不设置)
    poster: "", 
    
    // 视频简介 (支持 \n 换行)
    description: "随手制作的一个视频，随手制作的一个播放器。\n\n这是新的风格。现在头部拥有固定、半透明、模糊和圆角效果，按钮也采用了胶囊形设计。",

    // 侧边栏卡片列表
    sidebarCards: [
        {
            title: "关于视频",
            content: "本视频展示了面包的制作过程。"
        },
        {
            title: "相关推荐",
            // 内容支持 HTML，可以使用主题色类 .theme-text-color
            content: "<ul class='list-disc pl-5'><li><a href='#' class='theme-text-color hover:underline'>EV2 蛋糕制作</a></li><li><a href='#' class='theme-text-color hover:underline'>EV3 饼干教程</a></li></ul>"
        },
        {
            title: "公告",
            content: "新的播放器模板已经上线，采用了复古胶囊按钮和圆角头部设计！"
        }
    ]
};