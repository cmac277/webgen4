# Netlify Deployment Integration - Code Weaver

## 🎯 Overview

Code Weaver now supports generating **production-ready, Netlify-deployable projects** that create instant Deploy Preview URLs. This integration transforms the platform from a preview-only tool to a full deployment solution.

## 🏗️ Architecture

### **Previous Architecture:**
- FastAPI (Python) backend
- React frontend  
- MongoDB database
- Local file serving

### **New Netlify Architecture:**
- **Serverless Functions** (Node.js/TypeScript)
- React/Next.js or Vanilla HTML/CSS/JS frontend
- **API-based databases** (Supabase, FaunaDB, Firebase)
- Netlify CDN serving
- Instant Deploy Previews

## 📁 File Structure Generated

```
project-root/
├── index.html              # Frontend entry point
├── styles.css              # Styling
├── app.js                  # Client-side JavaScript
├── netlify.toml            # Netlify configuration (REQUIRED)
├── package.json            # Dependencies (if using npm)
├── README.md               # Project documentation
└── netlify/
    └── functions/          # Serverless backend functions
        ├── api.js          # Example API endpoint
        ├── contact.js      # Contact form handler
        └── ...
```

## 🔑 Key Features

### 1. **Netlify Functions Format**

All backend logic uses serverless functions:

```javascript
// netlify/functions/api.js
exports.handler = async (event, context) => {
    return {
        statusCode: 200,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: 'Hello from serverless!' })
    };
};
```

**Accessible at:** `https://your-site.netlify.app/.netlify/functions/api`

### 2. **netlify.toml Configuration**

Every project includes this critical file:

```toml
[build]
  publish = "dist"
  functions = "netlify/functions"

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200
```

### 3. **Environment Variables**

Projects specify required environment variables:

```javascript
// Access in Netlify Functions
const apiKey = process.env.SUPABASE_KEY;
const dbUrl = process.env.SUPABASE_URL;
```

These must be added in Netlify Dashboard → Site Settings → Environment Variables

### 4. **Database Integration**

Uses API-based, serverless-friendly databases:

**Supabase Example:**
```javascript
// netlify/functions/db-query.js
const { createClient } = require('@supabase/supabase-js');

exports.handler = async (event, context) => {
    const supabase = createClient(
        process.env.SUPABASE_URL,
        process.env.SUPABASE_KEY
    );
    
    const { data, error } = await supabase
        .from('users')
        .select('*');
    
    return {
        statusCode: 200,
        body: JSON.stringify(data)
    };
};
```

## 🚀 API Endpoints

### **Generate Netlify Project**

```http
POST /api/netlify/generate
Content-Type: application/json

{
  "session_id": "unique-session-id",
  "prompt": "Create a landing page for a coffee shop with menu and contact form",
  "model": "gpt-5",
  "edit_mode": false
}
```

**Response:**
```json
{
  "project_id": "uuid",
  "session_id": "unique-session-id",
  "files": {
    "index.html": "<!DOCTYPE html>...",
    "styles.css": "body { ... }",
    "app.js": "// JavaScript",
    "netlify.toml": "[build]\n  publish = \".\"",
    "netlify/functions/contact.js": "exports.handler = async ...",
    "package.json": "{ \"name\": \"project\" }",
    "README.md": "# Project"
  },
  "deploy_config": {
    "build_command": "npm run build",
    "publish_dir": "dist",
    "functions_dir": "netlify/functions",
    "environment_variables": {
      "SUPABASE_URL": "https://example.supabase.co",
      "SUPABASE_KEY": "placeholder-key"
    }
  },
  "created_at": "2025-11-23T07:31:44Z"
}
```

### **Get Latest Project**

```http
GET /api/netlify/session/{session_id}/latest
```

### **Download Project ZIP**

```http
POST /api/netlify/project/{project_id}/download
```

Returns base64-encoded ZIP file for download.

## 🎨 Frontend Integration

### **Making API Calls to Netlify Functions**

```javascript
// Frontend code
async function submitContactForm(data) {
    const response = await fetch('/.netlify/functions/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    
    return await response.json();
}
```

### **Environment Variables in Frontend**

For React/Next.js, use build-time variables:

```javascript
// Access Netlify environment variables
const apiUrl = process.env.REACT_APP_API_URL;
```

## 📦 Deployment Workflow

1. **Generate Project** → Call `/api/netlify/generate`
2. **Save to Git** → Code Weaver backend writes files to Git repository
3. **Connect to Netlify** → Repository linked to Netlify account
4. **Auto-Deploy** → Netlify detects push, builds, and deploys
5. **Deploy Preview URL** → Unique URL generated (e.g., `https://preview-abc123--site.netlify.app`)

## ✅ Validation & Requirements

### **Required Files:**
- ✅ `netlify.toml` - Configuration file
- ✅ `index.html` or entry point
- ✅ `package.json` (if using npm)

### **Function Requirements:**
- ✅ Located in `netlify/functions/` directory
- ✅ Exports `handler` async function
- ✅ Returns object with `statusCode`, `headers`, `body`

### **Database Requirements:**
- ✅ No persistent servers
- ✅ Use API-based services (Supabase, FaunaDB, Firebase)
- ✅ Environment variables for credentials

## 🔧 Technical Implementation

### **Backend Service** (`netlify_generator.py`)

```python
class NetlifyGenerator:
    async def generate_netlify_project(self, prompt, model, current_project):
        """
        Generates complete Netlify-compatible project
        Returns: Dict with files and deploy_config
        """
        # Analyze requirements
        analysis = await self._analyze_project_requirements(prompt)
        
        # Generate project structure
        if current_project:
            project = await self._edit_netlify_project(...)
        else:
            project = await self._create_netlify_project(...)
        
        # Validate Netlify requirements
        self._validate_netlify_project(project)
        
        return project
```

### **AI Prompt Engineering**

The system uses specialized prompts that enforce:
- Serverless-only architecture
- Netlify Functions format
- netlify.toml generation
- API-based database integration
- Environment variable management

## 🎯 Use Cases

### 1. **Static Websites**
- Landing pages
- Portfolios
- Documentation sites
- Simple HTML/CSS/JS projects

### 2. **Dynamic Web Apps**
- Contact forms with Netlify Functions
- Authentication with Supabase
- E-commerce with Stripe + Functions
- API integrations

### 3. **Full-Stack Applications**
- React/Next.js frontends
- Serverless APIs
- Database-backed apps
- Real-time features with WebSockets

## 📊 Output Format

Projects are returned as structured JSON:

```json
{
  "files": {
    "filepath": "content",
    "another/path/file.js": "content"
  },
  "deploy_config": {
    "build_command": "npm run build",
    "publish_dir": "dist",
    "functions_dir": "netlify/functions",
    "environment_variables": { }
  }
}
```

This format is ready for:
- Git repository commit
- ZIP file download
- Direct Netlify deployment

## 🐛 Troubleshooting

### **Issue: Functions not found**
**Solution:** Ensure `netlify.toml` specifies correct `functions` directory and files are in `netlify/functions/`

### **Issue: Build fails**
**Solution:** Check `build_command` in netlify.toml and ensure all dependencies in package.json

### **Issue: Environment variables undefined**
**Solution:** Add variables in Netlify Dashboard → Site Settings → Environment Variables

### **Issue: 502 errors from functions**
**Solution:** Check function logs in Netlify Dashboard → Functions → Select function → View logs

## 🚀 Future Enhancements

- [ ] Direct Netlify API integration for auto-deployment
- [ ] Real-time Deploy Preview URL generation
- [ ] Git repository auto-creation
- [ ] CI/CD pipeline configuration
- [ ] A/B testing support
- [ ] Edge Functions support
- [ ] Netlify Forms integration

## 📝 Notes

- **API Budget**: Current Emergent LLM API key has budget limitations. Increase budget for full AI-powered generation.
- **Fallback System**: When AI generation fails, system provides basic functional template.
- **Edit Mode**: Supports iterative development - subsequent prompts edit existing project.
- **Production Ready**: All generated code follows Netlify best practices and is deployment-ready.

## 🔗 Resources

- [Netlify Functions Documentation](https://docs.netlify.com/functions/overview/)
- [netlify.toml Reference](https://docs.netlify.com/configure-builds/file-based-configuration/)
- [Supabase Documentation](https://supabase.com/docs)
- [FaunaDB Documentation](https://docs.fauna.com/)

---

**Generated by Code Weaver | Powered by Netlify**
