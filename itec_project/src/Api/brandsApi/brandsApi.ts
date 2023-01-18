import {instance} from '../config';
import {BRANDS_URL} from './constants';
import {GetBrandsType, ResBrandType} from '../../types';

export const brandsAPI = {
    async setBrands({animalId = 6, categoryId}: GetBrandsType) {
        if (categoryId) {
            return await instance.get<Array<ResBrandType>>(`${BRANDS_URL}?animal=${animalId}&category=${categoryId}`);
        } else return await instance.get<Array<ResBrandType>>(`${BRANDS_URL}?animal=${animalId}`);
    },
}