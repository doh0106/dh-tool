#!/bin/bash

# pyproject.toml 파일에서 패키지 이름과 버전 추출
PACKAGE_NAME=$(grep -Po '(?<=name = ")[^"]*' pyproject.toml)
VERSION=$(grep -Po '(?<=version = ")[^"]*' pyproject.toml)

# 패키지 이름에서 하이픈(-)을 언더바(_)로 변환
MODULE_NAME=${PACKAGE_NAME//-/_}

# 출력 확인 (디버깅용)
echo "Original Package Name: $PACKAGE_NAME"
echo "Module Name (converted): $MODULE_NAME"
echo "Version: $VERSION"

# Build 패키지
python3 -m build

# Twine으로 업로드
python3 -m twine upload --repository pypi dist/"${MODULE_NAME}-${VERSION}-py3-none-any.whl"
