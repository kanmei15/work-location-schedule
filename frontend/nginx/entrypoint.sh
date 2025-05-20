#!/bin/sh

export CSP_CONNECT_SRC="$FRONTEND_ORIGIN $VITE_SERVER_BASE_URL $THIRDPARTY_URL"

# 環境変数から default.conf を生成
envsubst '$CSP_CONNECT_SRC' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf

# Nginx 起動
nginx -g 'daemon off;'
