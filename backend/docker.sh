#!/bin/bash

# 遇到任何错误时退出
set -e

# 配置
IMAGE_NAME="decipher-backend"
DOCKER_REGISTRY="mtwn105"
VERSION=$(git describe --tags --always)

# 构建Docker镜像
echo "正在构建Docker镜像..."
docker build -t $IMAGE_NAME:$VERSION .

# 为镜像标记latest标签
docker tag $IMAGE_NAME:$VERSION $DOCKER_REGISTRY/$IMAGE_NAME:latest
docker tag $IMAGE_NAME:$VERSION $DOCKER_REGISTRY/$IMAGE_NAME:$VERSION

# 推送镜像
echo "正在推送Docker镜像..."
docker push $DOCKER_REGISTRY/$IMAGE_NAME:latest
docker push $DOCKER_REGISTRY/$IMAGE_NAME:$VERSION

echo "成功构建并推送版本 $VERSION"
