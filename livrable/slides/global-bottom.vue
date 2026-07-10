<script setup lang="ts">
import { useNav } from '@slidev/client'
const { currentPage, total } = useNav()
</script>

<template>
  <footer
    v-if="currentPage > 1"
    class="absolute bottom-4 right-4 text-sm text-gray-400 opacity-70"
  >
    {{ currentPage }} / {{ total }}
  </footer>
</template>
