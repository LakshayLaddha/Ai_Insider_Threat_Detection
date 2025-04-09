#!/bin/bash

# Create React app
npx create-react-app .

# Install dependencies
npm install axios react-router-dom recharts @mui/material @mui/icons-material @emotion/react @emotion/styled

# Create directory structure
mkdir -p src/components src/pages src/services src/utils src/assets