<script setup lang="ts">
import { FormValidation } from '@/components/cmk-form/'
import { useValidation } from '../utils/validation'
import type { ValidationMessages } from '@/lib/validation'
import type { BooleanChoice } from '@/vue_formspec_components'

const props = defineProps<{
  spec: BooleanChoice
  backendValidation: ValidationMessages
}>()

const data = defineModel<boolean>('data', { required: true })
const [validation, value] = useValidation<boolean>(
  data,
  props.spec.validators,
  () => props.backendValidation
)
</script>

<template>
  <span class="checkbox">
    <input :id="$componentId" v-model="value" type="checkbox" />
    <label :for="$componentId">{{ props.spec.label }}</label>
  </span>
  <FormValidation :validation="validation"></FormValidation>
</template>
