<script setup lang="ts">
import { FormValidation } from '@/components/cmk-form/'
import type { Integer } from '@/vue_formspec_components'
import { useValidation } from '../utils/validation'
import { type ValidationMessages } from '@/lib/validation'

const props = defineProps<{
  spec: Integer
  backendValidation: ValidationMessages
}>()

const data = defineModel<number>('data', { required: true })
const [validation, value] = useValidation<number>(
  data,
  props.spec.validators,
  () => props.backendValidation
)
</script>

<template>
  <label v-if="props.spec.label" :for="$componentId">{{ props.spec.label }}</label>
  <input
    :id="$componentId"
    v-model="value"
    :placeholder="spec.input_hint || ''"
    class="number no-spinner"
    step="any"
    type="number"
  />
  <span v-if="props.spec.unit" class="vs_floating_text">{{ props.spec.unit }}</span>
  <FormValidation :validation="validation"></FormValidation>
</template>

<style scoped>
.no-spinner::-webkit-outer-spin-button,
.no-spinner::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.no-spinner[type='number'] {
  -moz-appearance: textfield;
}
</style>
