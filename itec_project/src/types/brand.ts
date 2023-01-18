export type BrandType = {
  id: number,
  name: string,
  image: string,
  chosen: boolean
}
export type ResBrandType = {
  id: number,
  name: string,
  image: string,
  // chosen: boolean -   question for brands.ts
}
export type SubcategoryType = {
  id: number,
  name: string,
  discount_subcategory: null
}
export type ResProductType = {
  id: number,
  name: string,
  subcategory: SubcategoryType[],
}
export type GetBrandsType = {
  animalId?: number | null,
  categoryId?: number | null,
}