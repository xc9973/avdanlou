# S3 STRM Generator - Makefile
# 支持构建、测试、清理和交叉编译

# 变量定义
BINARY_NAME := strm-generator
MODULE := strm-generator
CMD_PATH := ./cmd/strm-generator
BUILD_DIR := build
VERSION := $(shell git describe --tags --always --dirty 2>/dev/null || echo "dev")
BUILD_TIME := $(shell date -u '+%Y-%m-%d_%H:%M:%S')
LDFLAGS := -ldflags "-X main.version=$(VERSION) -X main.buildTime=$(BUILD_TIME)"

# Go 相关变量
GO := go
GOFLAGS := -v
GOTEST := $(GO) test
GOBUILD := $(GO) build

# 默认目标
.PHONY: all
all: build

# 构建本地二进制
.PHONY: build
build:
	@echo "Building $(BINARY_NAME)..."
	$(GOBUILD) $(GOFLAGS) $(LDFLAGS) -o $(BINARY_NAME) $(CMD_PATH)
	@echo "Build complete: $(BINARY_NAME)"

# 构建到 build 目录
.PHONY: build-dir
build-dir:
	@mkdir -p $(BUILD_DIR)
	$(GOBUILD) $(GOFLAGS) $(LDFLAGS) -o $(BUILD_DIR)/$(BINARY_NAME) $(CMD_PATH)

# 交叉编译 - Linux amd64
.PHONY: build-linux
build-linux:
	@echo "Cross-compiling for Linux amd64..."
	@mkdir -p $(BUILD_DIR)
	GOOS=linux GOARCH=amd64 $(GOBUILD) $(GOFLAGS) $(LDFLAGS) -o $(BUILD_DIR)/$(BINARY_NAME)-linux-amd64 $(CMD_PATH)
	@echo "Build complete: $(BUILD_DIR)/$(BINARY_NAME)-linux-amd64"

# 交叉编译 - Linux arm64
.PHONY: build-linux-arm64
build-linux-arm64:
	@echo "Cross-compiling for Linux arm64..."
	@mkdir -p $(BUILD_DIR)
	GOOS=linux GOARCH=arm64 $(GOBUILD) $(GOFLAGS) $(LDFLAGS) -o $(BUILD_DIR)/$(BINARY_NAME)-linux-arm64 $(CMD_PATH)
	@echo "Build complete: $(BUILD_DIR)/$(BINARY_NAME)-linux-arm64"

# 交叉编译 - macOS amd64
.PHONY: build-darwin
build-darwin:
	@echo "Cross-compiling for macOS amd64..."
	@mkdir -p $(BUILD_DIR)
	GOOS=darwin GOARCH=amd64 $(GOBUILD) $(GOFLAGS) $(LDFLAGS) -o $(BUILD_DIR)/$(BINARY_NAME)-darwin-amd64 $(CMD_PATH)
	@echo "Build complete: $(BUILD_DIR)/$(BINARY_NAME)-darwin-amd64"

# 交叉编译 - macOS arm64 (Apple Silicon)
.PHONY: build-darwin-arm64
build-darwin-arm64:
	@echo "Cross-compiling for macOS arm64..."
	@mkdir -p $(BUILD_DIR)
	GOOS=darwin GOARCH=arm64 $(GOBUILD) $(GOFLAGS) $(LDFLAGS) -o $(BUILD_DIR)/$(BINARY_NAME)-darwin-arm64 $(CMD_PATH)
	@echo "Build complete: $(BUILD_DIR)/$(BINARY_NAME)-darwin-arm64"

# 构建所有平台
.PHONY: build-all
build-all: build-linux build-linux-arm64 build-darwin build-darwin-arm64
	@echo "All builds complete!"

# 运行测试
.PHONY: test
test:
	@echo "Running tests..."
	$(GOTEST) $(GOFLAGS) ./...

# 运行测试并显示覆盖率
.PHONY: test-coverage
test-coverage:
	@echo "Running tests with coverage..."
	$(GOTEST) -coverprofile=coverage.out ./...
	$(GO) tool cover -html=coverage.out -o coverage.html
	@echo "Coverage report: coverage.html"

# 运行属性测试（更多迭代）
.PHONY: test-property
test-property:
	@echo "Running property-based tests..."
	$(GOTEST) -v -run "Property" ./...

# 清理构建产物
.PHONY: clean
clean:
	@echo "Cleaning..."
	rm -f $(BINARY_NAME)
	rm -rf $(BUILD_DIR)
	rm -f coverage.out coverage.html
	$(GO) clean
	@echo "Clean complete"

# 安装依赖
.PHONY: deps
deps:
	@echo "Installing dependencies..."
	$(GO) mod download
	$(GO) mod tidy

# 格式化代码
.PHONY: fmt
fmt:
	@echo "Formatting code..."
	$(GO) fmt ./...

# 代码检查
.PHONY: vet
vet:
	@echo "Running go vet..."
	$(GO) vet ./...

# 安装到 GOPATH/bin
.PHONY: install
install:
	@echo "Installing $(BINARY_NAME)..."
	$(GO) install $(LDFLAGS) $(CMD_PATH)

# 帮助信息
.PHONY: help
help:
	@echo "S3 STRM Generator - Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make              - Build for current platform"
	@echo "  make build        - Build for current platform"
	@echo "  make build-linux  - Cross-compile for Linux amd64"
	@echo "  make build-all    - Build for all platforms"
	@echo "  make test         - Run all tests"
	@echo "  make test-coverage- Run tests with coverage report"
	@echo "  make clean        - Remove build artifacts"
	@echo "  make deps         - Download and tidy dependencies"
	@echo "  make fmt          - Format code"
	@echo "  make vet          - Run go vet"
	@echo "  make install      - Install to GOPATH/bin"
	@echo "  make help         - Show this help"
