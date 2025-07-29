import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default {
  server: {
    proxy: {
      '/upload-schema': 'http://localhost:5000',
      '/generate-sql': 'http://localhost:5000',
      '/feedback': 'http://localhost:5000',

    },
  },
};
