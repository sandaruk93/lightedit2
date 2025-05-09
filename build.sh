#!/bin/bash
cd frontend
npm install --legacy-peer-deps
GENERATE_SOURCEMAP=false CI=false npm run build 