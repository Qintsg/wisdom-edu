/**
 * Markdown 渲染工具
 * 用于 AI 生成文本（聊天回复、知识点介绍、学习建议等）的格式化显示
 */
import { marked } from 'marked'

// 配置 marked
marked.setOptions({
    breaks: true,       // 换行符转 <br>
    gfm: true          // GitHub Flavored Markdown
})

/**
 * 将 Markdown 文本渲染为 HTML
 * @param {string} text - Markdown 文本
 * @returns {string} 渲染后的 HTML
 */
export function renderMarkdown(text) {
    if (!text) return ''
    try {
        return marked.parse(text)
    } catch {
        // 解析失败时回退到简单转换
        return text.replace(/\n/g, '<br>')
    }
}

/**
 * 将 Markdown 文本渲染为内联 HTML（不包裹 <p> 标签）
 * 适用于短文本，如标签、简短描述
 * @param {string} text
 * @returns {string}
 */
export function renderMarkdownInline(text) {
    if (!text) return ''
    try {
        return marked.parseInline(text)
    } catch {
        return text
    }
}
