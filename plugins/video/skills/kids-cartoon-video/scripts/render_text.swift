// Renders (multi-line, centered) text to a transparent PNG with an outline, using
// CoreText so complex scripts such as Khmer are shaped correctly.
// usage: render_text <text> <font> <sizePx> <fillHex> <outlineHex> <outlinePx> <out.png> [maxWidthPx]
// prints "<W>x<H> <padPx>"
import AppKit

let a = CommandLine.arguments
guard a.count == 8 || a.count == 9 else {
    FileHandle.standardError.write("usage: text font size fill outline outlinePx out.png\n".data(using: .utf8)!)
    exit(2)
}
let text = a[1].replacingOccurrences(of: "\\n", with: "\n")
let size = CGFloat(Double(a[3]) ?? 96)
let font = NSFont(name: a[2], size: size) ?? NSFont.boldSystemFont(ofSize: size)
func color(_ h: String) -> NSColor {
    var s = h; if s.hasPrefix("#") { s.removeFirst() }
    let v = UInt32(s, radix: 16) ?? 0
    return NSColor(srgbRed: CGFloat((v >> 16) & 255) / 255, green: CGFloat((v >> 8) & 255) / 255,
                   blue: CGFloat(v & 255) / 255, alpha: 1)
}
let outlinePx = CGFloat(Double(a[6]) ?? 0)
let para = NSMutableParagraphStyle(); para.alignment = .center; para.lineHeightMultiple = 0.82
var attrs: [NSAttributedString.Key: Any] = [.font: font, .paragraphStyle: para, .foregroundColor: color(a[4])]
let str = NSAttributedString(string: text, attributes: attrs)
let maxW = a.count == 9 ? CGFloat(Double(a[8]) ?? 4000) : 4000
let bounds = str.boundingRect(with: NSSize(width: maxW, height: 4000),
                              options: [.usesLineFragmentOrigin, .usesFontLeading])
let pad = outlinePx + size * 0.15
let W = Int(ceil(bounds.width + 2 * pad)), H = Int(ceil(bounds.height + 2 * pad))
let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: W, pixelsHigh: H, bitsPerSample: 8,
                           samplesPerPixel: 4, hasAlpha: true, isPlanar: false,
                           colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
NSGraphicsContext.saveGraphicsState()
NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)
let rect = NSRect(x: pad, y: pad, width: bounds.width, height: bounds.height)
if outlinePx > 0 {
    var o = attrs
    o[.strokeColor] = color(a[5])
    o[.strokeWidth] = outlinePx * 2 / size * 100   // positive = stroke only, % of font size
    NSAttributedString(string: text, attributes: o).draw(with: rect, options: [.usesLineFragmentOrigin, .usesFontLeading])
}
str.draw(with: rect, options: [.usesLineFragmentOrigin, .usesFontLeading])
NSGraphicsContext.restoreGraphicsState()
try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: a[7]))
print("\(W)x\(H) \(pad)")
