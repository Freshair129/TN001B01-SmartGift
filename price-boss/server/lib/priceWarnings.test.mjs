import { test } from 'node:test'
import assert from 'node:assert/strict'
import { priceTierWarnings } from './priceWarnings.mjs'

test('no warnings when price decreases smoothly with qty', () => {
  const warnings = priceTierWarnings([
    { qty: 100, unit_price: 500 },
    { qty: 300, unit_price: 470 },
    { qty: 500, unit_price: 450 },
  ])
  assert.deepEqual(warnings, [])
})

test('crit warning when a higher qty tier costs more than a lower one', () => {
  const warnings = priceTierWarnings([
    { qty: 100, unit_price: 400 },
    { qty: 300, unit_price: 450 },
  ])
  assert.equal(warnings.length, 1)
  assert.equal(warnings[0].level, 'crit')
  assert.match(warnings[0].message, /300 ชุดแพงกว่าสั่ง 100 ชุด/)
})

test('warn when price drops more than 25% between consecutive tiers', () => {
  const warnings = priceTierWarnings([
    { qty: 100, unit_price: 600 },
    { qty: 300, unit_price: 400 },
  ])
  assert.equal(warnings.length, 1)
  assert.equal(warnings[0].level, 'warn')
  assert.match(warnings[0].message, /ราคาตกลง 33%/)
})

test('rows with missing qty or unit_price are ignored', () => {
  const warnings = priceTierWarnings([
    { qty: 100, unit_price: null },
    { qty: null, unit_price: 500 },
    { qty: 100, unit_price: 500 },
    { qty: 300, unit_price: 480 },
  ])
  assert.deepEqual(warnings, [])
})

test('fewer than two valid rows produces no warnings and does not throw', () => {
  assert.deepEqual(priceTierWarnings([]), [])
  assert.deepEqual(priceTierWarnings([{ qty: 100, unit_price: 500 }]), [])
})

test('unsorted input is sorted by qty before comparing', () => {
  const warnings = priceTierWarnings([
    { qty: 300, unit_price: 450 },
    { qty: 100, unit_price: 400 },
  ])
  assert.equal(warnings.length, 1)
  assert.equal(warnings[0].level, 'crit')
})

test('zero-priced previous tier does not throw a division error', () => {
  assert.doesNotThrow(() =>
    priceTierWarnings([
      { qty: 100, unit_price: 0 },
      { qty: 300, unit_price: 50 },
    ]),
  )
})
