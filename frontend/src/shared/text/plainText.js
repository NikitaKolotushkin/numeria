export function stripInlineMarkdown(value) {
  return String(value || '')
    .replace(/`([^`]*)`/g, '$1')
    .replace(/\*\*([\s\S]*?)\*\*/g, '$1')
    .replace(/__([\s\S]*?)__/g, '$1')
    .replace(/(?<!\*)\*(?!\*)([^*\n]+)\*(?!\*)/g, '$1')
    .replace(/(?<!_)_(?!_)([^_\n]+)_(?!_)/g, '$1')
    .replace(/\*\*/g, '')
    .replace(/__/g, '')
    .replace(/[`*]/g, '')
    .replace(/#{3,}/g, '')
    .trim()
}

export function theoryParts(source) {
  const chunks = String(source || '')
    .split(/\n\s*\n/)
    .map((chunk) => chunk.trim())
    .filter(Boolean)
  if (!chunks.length) return []
  return chunks.map((chunk) => {
    const lines = chunk.split('\n')
    if (/^\s{0,3}#{1,6}\s+/.test(lines[0])) {
      return {
        heading: stripInlineMarkdown(lines[0].replace(/^\s{0,3}#{1,6}\s+/, '')),
        text: stripInlineMarkdown(lines.slice(1).join('\n'))
      }
    }
    return { heading: '', text: stripInlineMarkdown(chunk) }
  })
}
