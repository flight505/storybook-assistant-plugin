#!/usr/bin/env bash
# Detect frontend framework and configuration from package.json
# Returns: framework name, version, and bundler (vite/webpack)

set -e

PACKAGE_JSON="package.json"

if [ ! -f "$PACKAGE_JSON" ]; then
    echo "ERROR: package.json not found"
    exit 1
fi

# Detect framework by checking dependencies
detect_framework() {
    local pkg_content=$(cat "$PACKAGE_JSON")

    # Check for Next.js
    if echo "$pkg_content" | grep -q '"next"'; then
        FRAMEWORK="nextjs"
        VERSION=$(echo "$pkg_content" | grep '"next":' | sed 's/.*: "[\^~]*//' | sed 's/".*//')
        echo "FRAMEWORK=nextjs"
        echo "VERSION=$VERSION"

        # Check if using Vite (Next.js with Vite support in 14+)
        if echo "$pkg_content" | grep -q '"@next/vite"'; then
            echo "BUNDLER=vite"
        else
            echo "BUNDLER=webpack"
        fi
        return 0
    fi

    # Check for React
    if echo "$pkg_content" | grep -q '"react"'; then
        FRAMEWORK="react"
        VERSION=$(echo "$pkg_content" | grep '"react":' | sed 's/.*: "[\^~]*//' | sed 's/".*//')
        echo "FRAMEWORK=react"
        echo "VERSION=$VERSION"

        # Detect bundler
        if echo "$pkg_content" | grep -q '"vite"'; then
            echo "BUNDLER=vite"
        elif echo "$pkg_content" | grep -q '"webpack"'; then
            echo "BUNDLER=webpack"
        elif echo "$pkg_content" | grep -q '"@vitejs/plugin-react"'; then
            echo "BUNDLER=vite"
        else
            echo "BUNDLER=unknown"
        fi
        return 0
    fi

    # Check for Vue
    if echo "$pkg_content" | grep -q '"vue"'; then
        FRAMEWORK="vue"
        VERSION=$(echo "$pkg_content" | grep '"vue":' | sed 's/.*: "[\^~]*//' | sed 's/".*//')
        echo "FRAMEWORK=vue"
        echo "VERSION=$VERSION"

        # Detect bundler
        if echo "$pkg_content" | grep -q '"vite"'; then
            echo "BUNDLER=vite"
        elif echo "$pkg_content" | grep -q '"webpack"'; then
            echo "BUNDLER=webpack"
        elif echo "$pkg_content" | grep -q '"@vitejs/plugin-vue"'; then
            echo "BUNDLER=vite"
        else
            echo "BUNDLER=unknown"
        fi
        return 0
    fi

    # Check for Svelte
    if echo "$pkg_content" | grep -q '"svelte"'; then
        FRAMEWORK="svelte"
        VERSION=$(echo "$pkg_content" | grep '"svelte":' | sed 's/.*: "[\^~]*//' | sed 's/".*//')
        echo "FRAMEWORK=svelte"
        echo "VERSION=$VERSION"

        # Svelte typically uses Vite
        if echo "$pkg_content" | grep -q '"vite"'; then
            echo "BUNDLER=vite"
        elif echo "$pkg_content" | grep -q '"@sveltejs/vite-plugin-svelte"'; then
            echo "BUNDLER=vite"
        else
            echo "BUNDLER=unknown"
        fi
        return 0
    fi

    # Check for Angular
    if echo "$pkg_content" | grep -q '"@angular/core"'; then
        FRAMEWORK="angular"
        VERSION=$(echo "$pkg_content" | grep '"@angular/core":' | sed 's/.*: "[\^~]*//' | sed 's/".*//')
        echo "FRAMEWORK=angular"
        echo "VERSION=$VERSION"
        echo "BUNDLER=webpack"  # Angular uses webpack by default
        return 0
    fi

    # Check for Solid.js
    if echo "$pkg_content" | grep -q '"solid-js"'; then
        FRAMEWORK="solid"
        VERSION=$(echo "$pkg_content" | grep '"solid-js":' | sed 's/.*: "[\^~]*//' | sed 's/".*//')
        echo "FRAMEWORK=solid"
        echo "VERSION=$VERSION"

        if echo "$pkg_content" | grep -q '"vite"'; then
            echo "BUNDLER=vite"
        else
            echo "BUNDLER=unknown"
        fi
        return 0
    fi

    # Check for Lit
    if echo "$pkg_content" | grep -q '"lit"'; then
        FRAMEWORK="lit"
        VERSION=$(echo "$pkg_content" | grep '"lit":' | sed 's/.*: "[\^~]*//' | sed 's/".*//')
        echo "FRAMEWORK=lit"
        echo "VERSION=$VERSION"

        if echo "$pkg_content" | grep -q '"vite"'; then
            echo "BUNDLER=vite"
        else
            echo "BUNDLER=unknown"
        fi
        return 0
    fi

    # Unknown framework
    echo "FRAMEWORK=unknown"
    echo "VERSION=unknown"
    echo "BUNDLER=unknown"
    return 1
}

# Detect platform-specific setup (Tauri or Electron)
detect_platform() {
    local pkg_content=$(cat "$PACKAGE_JSON")

    # Check for Tauri
    if echo "$pkg_content" | grep -q '"@tauri-apps/api"' || [ -f "src-tauri/tauri.conf.json" ]; then
        echo "PLATFORM=tauri"
        if [ -f "src-tauri/Cargo.toml" ]; then
            TAURI_VERSION=$(grep "tauri =" src-tauri/Cargo.toml | sed 's/.*= "//' | sed 's/".*//')
            echo "PLATFORM_VERSION=$TAURI_VERSION"
        fi
        return 0
    fi

    # Check for Electron
    if echo "$pkg_content" | grep -q '"electron"'; then
        echo "PLATFORM=electron"
        ELECTRON_VERSION=$(echo "$pkg_content" | grep '"electron":' | sed 's/.*: "[\^~]*//' | sed 's/".*//')
        echo "PLATFORM_VERSION=$ELECTRON_VERSION"
        return 0
    fi

    echo "PLATFORM=web"
    return 0
}

# Detect design system
detect_design_system() {
    local pkg_content=$(cat "$PACKAGE_JSON")

    if echo "$pkg_content" | grep -q '"@mui/material"'; then
        echo "DESIGN_SYSTEM=mui"
    elif echo "$pkg_content" | grep -q '"antd"'; then
        echo "DESIGN_SYSTEM=antd"
    elif echo "$pkg_content" | grep -q '"@radix-ui"' && echo "$pkg_content" | grep -q '"tailwindcss"'; then
        echo "DESIGN_SYSTEM=shadcn"
    elif echo "$pkg_content" | grep -q '"@chakra-ui/react"'; then
        echo "DESIGN_SYSTEM=chakra"
    elif echo "$pkg_content" | grep -q '"@mantine/core"'; then
        echo "DESIGN_SYSTEM=mantine"
    else
        echo "DESIGN_SYSTEM=custom"
    fi
}

# Main execution
detect_framework
detect_platform
detect_design_system

exit 0
