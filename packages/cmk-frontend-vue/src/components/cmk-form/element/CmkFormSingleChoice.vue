<script setup lang="ts">
import { FormValidation } from '@/components/cmk-form/'
import type { SingleChoice } from '@/vue_formspec_components'
import { useValidation } from '../utils/validation'
import { type ValidationMessages } from '@/lib/validation'

const props = defineProps<{
  spec: SingleChoice
  backendValidation: ValidationMessages
}>()

const data = defineModel('data', { type: String, required: true })
const [validation, value] = useValidation<string>(
  data,
  props.spec.validators,
  () => props.backendValidation
)
</script>

<template>
  <div>
    <label v-if="$props.spec.label" :for="$componentId">{{ spec.label }}</label>
    <select :id="$componentId" v-model="value" :disabled="spec.frozen">
      <option
        v-for="element in spec.elements"
        :key="JSON.stringify(element.name)"
        :value="element.name"
      >
        {{ element.title }}
      </option>
    </select>
  </div>
  <FormValidation :validation="validation"></FormValidation>
</template>
