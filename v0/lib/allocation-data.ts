// Types and sample/mock data for the RAW MAT Allocation Engine UI.
// This is a UI/style reference build: the "run" produces plausible sample
// output rather than executing the real two-stage allocation algorithm.

export type MappingRow = {
  source: string
  column: string
  meaning: string
  detected: string
}

export type ConversionRow = {
  id: string
  motherUnit: string
  childUnit: string
  ratio: string
}

export type SizeConversionRow = {
  id: string
  suffix: string
  childUnit: string
  ratio: string
}

export type ResultRow = {
  cutting: string
  so: string
  motherMaterial: string
  motherUnit: string
  childMaterial: string
  childUnit: string
  demandQty: number
  providedQty: number
  remainingStock: number
  allocated: string
}

export const RESULT_HEADERS = [
  'Cutting',
  'SO',
  'Mother material',
  'Mother unit (2.R)',
  'Child material',
  'Child unit (3.M)',
  'Demand qty',
  'Provided qty',
  'Remaining stock',
  'Allocated (Y)',
] as const

export const DEFAULT_MAPPING: MappingRow[] = [
  { source: 'Excel 1', column: 'A', meaning: 'SO (order no.)', detected: 'so' },
  { source: 'Excel 1', column: 'B', meaning: 'Cutting date', detected: 'cutting' },
  { source: 'Excel 2', column: 'F', meaning: 'Mother material', detected: 'mother_code' },
  { source: 'Excel 2', column: 'R', meaning: 'Mother unit', detected: 'uom' },
  { source: 'Excel 3', column: 'F', meaning: 'Mother name / suffix', detected: 'name' },
  { source: 'Excel 3', column: 'H', meaning: 'Match key', detected: 'match_key' },
  { source: 'Excel 3', column: 'M', meaning: 'Child unit', detected: 'child_uom' },
  { source: 'Excel 3', column: 'Q', meaning: 'Child demand qty', detected: 'qty' },
]

export const DEFAULT_CONVERSIONS: ConversionRow[] = [
  { id: 'c1', motherUnit: 'M', childUnit: 'YD', ratio: '1.0936' },
  { id: 'c2', motherUnit: 'YD', childUnit: 'M', ratio: '0.9144' },
]

export const DEFAULT_SIZE_CONVERSIONS: SizeConversionRow[] = [
  { id: 's1', suffix: '44"', childUnit: 'YD', ratio: '1.2222' },
  { id: 's2', suffix: '58"', childUnit: 'YD', ratio: '1.6111' },
  { id: 's3', suffix: '60"', childUnit: 'M', ratio: '1.5240' },
]

export const SAMPLE_EXCEL_1 = `so\tcutting
SO-A\t2026-07-01
SO-B\t2026-07-03
SO-A\t2026-07-10`

export const SAMPLE_EXCEL_2 = `mother_code\tuom
FAB-BLUE-01\tM
FAB-GREY-02\tYD
FAB-KHAKI-03\tSHT`

export const SAMPLE_EXCEL_3 = `name\tmatch_key\tchild_uom\tqty
Blue Twill 58"\tK-01\tYD\t420
Grey Melange 60"\tK-02\tM\t185
Khaki Canvas 44"\tK-03\tYD\t96`

const SAMPLE_RESULTS: ResultRow[] = [
  { cutting: '2026-07-01', so: 'SO-A', motherMaterial: 'FAB-BLUE-01', motherUnit: 'M', childMaterial: 'Blue Twill 58"', childUnit: 'YD', demandQty: 420, providedQty: 420, remainingStock: 180, allocated: 'Y' },
  { cutting: '2026-07-01', so: 'SO-A', motherMaterial: 'FAB-GREY-02', motherUnit: 'YD', childMaterial: 'Grey Melange 60"', childUnit: 'M', demandQty: 185, providedQty: 185, remainingStock: 42, allocated: 'Y' },
  { cutting: '2026-07-03', so: 'SO-B', motherMaterial: 'FAB-KHAKI-03', motherUnit: 'SHT', childMaterial: 'Khaki Canvas 44"', childUnit: 'YD', demandQty: 96, providedQty: 60, remainingStock: 0, allocated: 'Y' },
  { cutting: '2026-07-03', so: 'SO-B', motherMaterial: 'FAB-BLUE-01', motherUnit: 'M', childMaterial: 'Blue Twill 58"', childUnit: 'YD', demandQty: 310, providedQty: 310, remainingStock: 0, allocated: 'Y' },
  { cutting: '2026-07-10', so: 'SO-A', motherMaterial: 'FAB-GREY-02', motherUnit: 'YD', childMaterial: 'Grey Melange 60"', childUnit: 'M', demandQty: 240, providedQty: 210, remainingStock: 0, allocated: 'Y' },
  { cutting: '2026-07-10', so: 'SO-A', motherMaterial: 'FAB-KHAKI-03', motherUnit: 'SHT', childMaterial: 'Khaki Canvas 44"', childUnit: 'YD', demandQty: 0, providedQty: 0, remainingStock: 24, allocated: '' },
  { cutting: '2026-07-12', so: 'SO-C', motherMaterial: 'FAB-BLUE-01', motherUnit: 'M', childMaterial: 'Blue Twill 58"', childUnit: 'YD', demandQty: 150, providedQty: 150, remainingStock: 30, allocated: 'Y' },
  { cutting: '2026-07-12', so: 'SO-C', motherMaterial: 'FAB-GREY-02', motherUnit: 'YD', childMaterial: 'Grey Melange 60"', childUnit: 'M', demandQty: 275, providedQty: 190, remainingStock: 0, allocated: 'Y' },
]

export type AllocationResult = {
  rows: ResultRow[]
  stats: {
    rowsExported: number
    demandKeys: number
    mothersMatched: number
    shortage: number
  }
}

// Returns the full mock allocation result set.
export function runMockAllocation(): AllocationResult {
  const rows = SAMPLE_RESULTS
  const mothers = new Set(rows.map((r) => r.motherMaterial))
  const demandKeys = new Set(rows.map((r) => `${r.so}|${r.childMaterial}`))
  const shortage = rows.filter((r) => r.providedQty < r.demandQty).length
  return {
    rows,
    stats: {
      rowsExported: rows.length,
      demandKeys: demandKeys.size,
      mothersMatched: mothers.size,
      shortage,
    },
  }
}
