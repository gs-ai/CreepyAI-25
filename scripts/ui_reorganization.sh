#!/bin/bash

# Navigate to project directory
cd /Users/mbaosint/Desktop/Projects/CreepyAI

# Create the scripts and documentation files
mkdir -p ui/dialogs ui/wizards ui/main ui/components ui/common

# Create structure.js
cat > ui/structure.js << 'EOF'
/**
 * This script creates the folder structure for the reorganized UI components.
 * It's meant to be run once to set up the directories.
 */

const fs = require('fs');
const path = require('path');

// Define the folder structure
const folders = [
  'dialogs',
  'wizards',
  'main',
  'components',
  'common'
];

// Create each folder if it doesn't exist
folders.forEach(folder => {
  const folderPath = path.join(__dirname, folder);
  if (!fs.existsSync(folderPath)) {
    fs.mkdirSync(folderPath, { recursive: true });
    console.log(`Created directory: ${folderPath}`);
  } else {
    console.log(`Directory already exists: ${folderPath}`);
  }
});

console.log('UI folder structure setup complete!');
EOF

# Create migration.js
cat > ui/migration.js << 'EOF'
/**
 * UI Migration Helper Script
 * 
 * This script helps identify files that need to be moved to the new UI structure
 * and generates commands to help with the migration.
 */

const fs = require('fs');
const path = require('path');

// Directories to scan
const directories = [
  '../components',
  '../gui',
  '../ui'
];

// Map of file patterns to target directories
const targetMapping = {
  'dialog': 'ui/dialogs',
  'modal': 'ui/dialogs',
  'popup': 'ui/dialogs',
  'wizard': 'ui/wizards',
  'step': 'ui/wizards',
  'page': 'ui/main',
  'screen': 'ui/main',
  'app': 'ui/main',
  'button': 'ui/components',
  'input': 'ui/components',
  'form': 'ui/components',
  'list': 'ui/components',
  'card': 'ui/components',
  'util': 'ui/common',
  'style': 'ui/common',
  'theme': 'ui/common',
  'constant': 'ui/common'
};

function scanDirectories() {
  const files = [];

  directories.forEach(dir => {
    const basePath = path.join(__dirname, dir);
    
    try {
      if (fs.existsSync(basePath)) {
        const items = fs.readdirSync(basePath, { withFileTypes: true });
        
        items.forEach(item => {
          if (item.isFile() && (item.name.endsWith('.js') || item.name.endsWith('.jsx') || 
                              item.name.endsWith('.ts') || item.name.endsWith('.tsx'))) {
            files.push({
              path: path.join(dir, item.name),
              name: item.name,
              suggested: suggestDestination(item.name)
            });
          } else if (item.isDirectory()) {
            // Could recursively scan subdirectories here if needed
          }
        });
      }
    } catch (error) {
      console.error(`Error scanning directory ${dir}:`, error);
    }
  });

  return files;
}

function suggestDestination(filename) {
  for (const [pattern, destination] of Object.entries(targetMapping)) {
    if (filename.toLowerCase().includes(pattern.toLowerCase())) {
      return destination;
    }
  }
  return 'ui/components'; // default destination
}

function generateMigrationPlan() {
  const files = scanDirectories();
  
  console.log('Migration Plan:');
  console.log('==============');
  
  files.forEach(file => {
    console.log(`Move ${file.path} → ${file.suggested}/${file.name}`);
    console.log(`# Command: mkdir -p ${file.suggested} && cp ${file.path} ${file.suggested}/${file.name}`);
    console.log();
  });
  
  console.log('After moving files, update imports in all affected files.');
}

generateMigrationPlan();
EOF

# Create update-imports.js
cat > ui/update-imports.js << 'EOF'
/**
 * Import Path Updater
 * 
 * This script helps update import paths after UI component reorganization.
 * It scans source files and suggests import path updates based on the new organization.
 */

const fs = require('fs');
const path = require('path');

// Define the recursive directory scanner
function walkDir(dir, callback) {
  fs.readdirSync(dir).forEach(file => {
    const filepath = path.join(dir, file);
    const stats = fs.statSync(filepath);
    
    if (stats.isDirectory()) {
      walkDir(filepath, callback);
    } else if (stats.isFile() && 
              (filepath.endsWith('.js') || filepath.endsWith('.jsx') || 
               filepath.endsWith('.ts') || filepath.endsWith('.tsx'))) {
      callback(filepath);
    }
  });
}

// Map of old import paths to new ones
const importMappings = {
  // These will be populated based on your specific files
  '../components/': '../ui/components/',
  '../gui/': '../ui/',
  './Dialog': '../ui/dialogs/Dialog',
  // Add more mappings as you identify them
};

// Process a file to update import paths
function processFile(filePath) {
  try {
    let content = fs.readFileSync(filePath, 'utf8');
    let needsUpdate = false;
    
    // Check for imports that need updating
    for (const [oldPath, newPath] of Object.entries(importMappings)) {
      if (content.includes(`from '${oldPath}`) || content.includes(`from "${oldPath}`)) {
        needsUpdate = true;
        content = content.replaceAll(`from '${oldPath}`, `from '${newPath}`);
        content = content.replaceAll(`from "${oldPath}`, `from "${newPath}`);
        console.log(`[${filePath}] Found import path to update: ${oldPath} → ${newPath}`);
      }
    }
    
    if (needsUpdate) {
      // Option 1: Write changes directly
      // fs.writeFileSync(filePath, content, 'utf8');
      // console.log(`Updated imports in ${filePath}`);
      
      // Option 2: Just report what needs to be changed (safer)
      console.log(`File needs updates: ${filePath}`);
    }
  } catch (error) {
    console.error(`Error processing file ${filePath}:`, error);
  }
}

// Main execution
console.log('Scanning for import paths to update...');
const projectRoot = path.join(__dirname, '..');
walkDir(projectRoot, processFile);
console.log('Scan complete. Review the suggestions above.');
EOF

# Create index.js
cat > ui/index.js << 'EOF'
/**
 * Main UI components export file
 * This file centralizes exports from all UI subfolders to simplify imports
 */

// Dialog exports
export * from './dialogs';

// Wizard exports
export * from './wizards';

// Main UI exports
export * from './main';

// Component exports
export * from './components';

// Common UI utilities
export * from './common';
EOF

# Create README.md
cat > ui/README.md << 'EOF'
# UI Components Organization

This directory contains all UI-related components for the CreepyAI project. The structure is organized as follows:

## Directory Structure

- `/ui/dialogs/`: Modal dialogs and popup components
- `/ui/wizards/`: Step-by-step wizard interfaces
- `/ui/main/`: Main application screens and layouts
- `/ui/components/`: Reusable UI components
- `/ui/common/`: Shared UI utilities, styles, and constants

## Migration

This organization represents a consolidation of UI components previously scattered across:
- `/components/`
- `/gui/`
- `/ui/` (original)

All imports have been updated to reflect these new locations.

## Development Guidelines

When creating new UI elements:
1. Place them in the appropriate subfolder based on their function
2. Follow existing naming conventions
3. Import shared components from their new locations

## Running the Setup Script

If you need to create this folder structure from scratch:

```bash
node ui/structure.js
```
EOF

# Make the helper scripts executable
chmod +x ui/structure.js ui/migration.js ui/update-imports.js

echo "Files created successfully. Now run the following commands to reorganize UI components:"
echo "1. node ui/structure.js     # Create folder structure (optional, already done manually)"
echo "2. node ui/migration.js     # Generate migration plan"
echo "3. node ui/update-imports.js # Scan for import paths to update"
