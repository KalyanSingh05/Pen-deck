#!/bin/bash

# Bettercap Installation Script for Raspberry Pi
# Multiple installation methods

echo "🔧 Installing Bettercap for Raspberry Pi..."

# Method 1: Try direct binary download (corrected URLs)
install_binary() {
    echo "Attempting binary installation..."
    
    # Try different possible URLs for ARM binaries
    URLS=(
        "https://github.com/bettercap/bettercap/releases/download/v2.32.0/bettercap-v2.32.0-linux-arm.zip"
        "https://github.com/bettercap/bettercap/releases/download/v2.32.0/bettercap_v2.32.0_linux_arm.tar.gz"
        "https://github.com/bettercap/bettercap/releases/latest/download/bettercap_linux_arm.zip"
    )
    
    for url in "${URLS[@]}"; do
        echo "Trying: $url"
        if wget "$url" -O bettercap_download 2>/dev/null; then
            echo "Download successful from: $url"
            
            # Extract based on file type
            if [[ "$url" == *.zip ]]; then
                if unzip bettercap_download 2>/dev/null; then
                    if [ -f "bettercap" ]; then
                        sudo mv bettercap /usr/local/bin/
                        sudo chmod +x /usr/local/bin/bettercap
                        sudo setcap cap_net_raw,cap_net_admin=eip /usr/local/bin/bettercap
                        rm -f bettercap_download
                        echo "✅ Bettercap installed successfully via binary"
                        return 0
                    fi
                fi
            elif [[ "$url" == *.tar.gz ]]; then
                if tar -xzf bettercap_download 2>/dev/null; then
                    if [ -f "bettercap" ]; then
                        sudo mv bettercap /usr/local/bin/
                        sudo chmod +x /usr/local/bin/bettercap
                        sudo setcap cap_net_raw,cap_net_admin=eip /usr/local/bin/bettercap
                        rm -f bettercap_download
                        echo "✅ Bettercap installed successfully via binary"
                        return 0
                    fi
                fi
            fi
            rm -f bettercap_download
        fi
    done
    
    echo "❌ Binary installation failed"
    return 1
}

# Method 2: Build from source with modern Go
install_from_source() {
    echo "Attempting source installation..."
    
    # Check if we have a modern Go version
    if command -v go &> /dev/null; then
        GO_VERSION=$(go version | grep -oP 'go\K[0-9]+\.[0-9]+')
        echo "Found Go version: $GO_VERSION"
        
        # If Go version is too old, try to install newer version
        if [[ $(echo "$GO_VERSION < 1.16" | bc -l 2>/dev/null || echo "1") == "1" ]]; then
            echo "Go version too old, installing newer version..."
            install_modern_go
        fi
    else
        echo "Go not found, installing..."
        install_modern_go
    fi
    
    # Try building with Go modules
    export GO111MODULE=on
    export GOPROXY=direct
    
    # Create temporary directory
    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"
    
    # Clone and build
    if git clone https://github.com/bettercap/bettercap.git; then
        cd bettercap
        if go build -o bettercap .; then
            sudo mv bettercap /usr/local/bin/
            sudo chmod +x /usr/local/bin/bettercap
            sudo setcap cap_net_raw,cap_net_admin=eip /usr/local/bin/bettercap
            cd /
            rm -rf "$TEMP_DIR"
            echo "✅ Bettercap installed successfully from source"
            return 0
        fi
    fi
    
    cd /
    rm -rf "$TEMP_DIR"
    echo "❌ Source installation failed"
    return 1
}

# Method 3: Install modern Go
install_modern_go() {
    echo "Installing modern Go version..."
    
    # Remove old Go
    sudo rm -rf /usr/local/go
    
    # Download and install Go 1.19 for ARM
    GO_VERSION="1.19.13"
    GO_ARCHIVE="go${GO_VERSION}.linux-armv6l.tar.gz"
    
    if wget "https://golang.org/dl/${GO_ARCHIVE}"; then
        sudo tar -C /usr/local -xzf "$GO_ARCHIVE"
        rm "$GO_ARCHIVE"
        
        # Update PATH
        echo 'export PATH=$PATH:/usr/local/go/bin' | sudo tee -a /etc/profile
        echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
        export PATH=$PATH:/usr/local/go/bin
        
        echo "✅ Modern Go installed"
        return 0
    else
        echo "❌ Failed to download Go"
        return 1
    fi
}

# Method 4: Use package manager (if available)
install_via_package() {
    echo "Attempting package manager installation..."
    
    # Try snap if available
    if command -v snap &> /dev/null; then
        if sudo snap install bettercap; then
            echo "✅ Bettercap installed via snap"
            return 0
        fi
    fi
    
    echo "❌ Package manager installation failed"
    return 1
}

# Main installation logic
main() {
    # Check if already installed
    if command -v bettercap &> /dev/null; then
        echo "✅ Bettercap is already installed"
        bettercap -version
        exit 0
    fi
    
    # Try installation methods in order
    if install_binary; then
        exit 0
    elif install_from_source; then
        exit 0
    elif install_via_package; then
        exit 0
    else
        echo "❌ All installation methods failed"
        echo ""
        echo "Manual installation options:"
        echo "1. Download binary manually from: https://github.com/bettercap/bettercap/releases"
        echo "2. Build from source after installing Go 1.16+"
        echo "3. Use Docker: docker run -it --privileged --net=host bettercap/bettercap"
        echo ""
        echo "Pen-Deck will work without Bettercap - you can install it later"
        exit 1
    fi
}

# Run main function
main
