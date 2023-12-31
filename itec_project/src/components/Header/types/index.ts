import { ProductItemType } from '../../../types';

export type SearchResultsBlockType = {
  productItems: Array<ProductItemType>,
  onButtonClick: () => void,
  onProductItemClick: ( id: number ) => void
}
export type HeaderBurgerPropsType = {
  onClickHandler: () => void,
  forFilters: boolean
}