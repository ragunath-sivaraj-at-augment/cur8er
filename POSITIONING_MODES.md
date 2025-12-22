# Template Positioning Modes

The Cur8er template editor now supports **template-level positioning modes**. When you create a template, you choose ONE mode for the entire template, and all elements (including default elements) will use that mode.

## 🎯 How It Works

**When creating a new template**, you select:
- **📍 Pixel Mode** - All elements use exact X,Y coordinates
- **🎯 Zone Mode** - All elements use semantic zones with AI awareness

All default elements and any new elements you add will automatically follow the template's chosen mode.

## 📍 Pixel Mode (Precise Positioning)

**Use when:** You need exact control over element placement

### Features:
- Specify exact X,Y coordinates
- Full pixel-perfect precision
- Visual preview with exact placement
- Best for finalized designs

### Example JSON:
```json
{
  "type": "text",
  "position": {
    "x": 480,
    "y": 50
  },
  "size": {
    "width": 960,
    "height": 135
  },
  "content": "{{client_name}}"
}
```

---

## 🎯 Zone Mode (Semantic + AI-Aware)

**Use when:** You want AI to generate backgrounds that integrate with your text placement

### Features:
- Semantic zone selection (top-left, center, bottom-right, etc.)
- Style hints guide AI background generation
- Integration descriptions for cohesive visuals
- AI-aware spatial positioning

### Available Zones:
- `top-left`, `top-center`, `top-right`
- `center-left`, `center`, `center-right`
- `bottom-left`, `bottom-center`, `bottom-right`

### Example JSON:
```json
{
  "type": "text",
  "position": {
    "zone": "top-left",
    "style": "blended, subtle",
    "integration": "naturally part of environment"
  },
  "size": {
    "width": 400,
    "height": 100
  },
  "content": "{{client_name}}"
}
```

---

## 🎨 How Zone Mode Helps AI

When you use zone-based positioning:

1. **Spatial Awareness**: AI knows where text will appear
2. **Style Integration**: AI uses your style hints (blended, bold, subtle)
3. **Natural Composition**: AI creates backgrounds that make text feel part of the scene
4. **Lighting & Depth**: AI generates matching lighting, shadows, and atmosphere

Example AI prompt generated from zone positioning:
```
"Create a Christmas scene with:
- logo in top-left (style: blended) (naturally part of environment)
- text in center (style: bold, prominent) (integrated with scene lighting)

All text and logos should appear as part of the scene, with matching 
lighting, color grading, glow, and depth. Avoid flat UI overlays."
```

---

## 🔀 Template Consistency

**Important:** Each template uses ONE positioning mode throughout:
- Pixel templates → all elements have X,Y coordinates
- Zone templates → all elements have zone assignments

**You cannot mix modes within a single template.** This ensures:
- ✅ Consistent behavior across all elements
- ✅ Clear AI awareness for zone-based templates
- ✅ Predictable positioning for pixel-based templates

---

## 🛠️ Using the Template Editor

### Creating a New Template:
1. Select "Create New Template"
2. Enter template name and dimensions
3. **Choose positioning mode:**
   - **📍 Pixel Mode** for exact X,Y coordinate control
   - **🎯 Zone Mode** for semantic, AI-aware positioning
4. Click "Create Template"
5. Default elements are created using your chosen mode

### Adding Elements:
- Elements automatically use the template's positioning mode
- **Pixel mode templates** → Enter X,Y coordinates
- **Zone mode templates** → Select zone + add style hints

### Editing Elements:
- View element position in the format of the template's mode
- Delete and re-add elements if repositioning is needed
- All elements maintain consistency with template mode

---

## 📊 Comparison

| Feature | Pixel Mode | Zone Mode |
|---------|-----------|-----------|
| Precision | Exact (pixel-perfect) | Approximate (zone-based) |
| AI Integration | No awareness | Full spatial awareness |
| Use Case | Final designs | Dynamic AI layouts |
| Visual Control | Complete | Semantic |
| Background Gen | Standard | Context-aware |
| Template Consistency | ✅ All elements pixel | ✅ All elements zone |
| Mix Modes | ❌ No (one mode per template) | ❌ No (one mode per template) |

---

## 💡 Best Practices

### Use Pixel Mode for:
- Brand logos with exact placement requirements
- Precise button positioning
- Fixed layouts that never change
- Designs with strict visual guidelines
- Production templates with specific measurements

### Use Zone Mode for:
- Dynamic content with varying lengths
- AI-generated backgrounds that integrate with text
- Quick prototyping and iteration
- Layouts where text should blend naturally with AI art
- Experimentation with different compositions

### Migration Strategy:
Want to try zone mode with an existing pixel template?
1. Create a new template with zone mode
2. Recreate key elements using zones
3. Compare results from both templates
4. Keep both versions for different use cases!
