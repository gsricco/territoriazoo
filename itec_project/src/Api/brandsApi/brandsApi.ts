import {instance} from '../config';
import {BRANDS_URL} from './constants';
import {GetBrandsType, ResBrandType} from '../../types';

export const brandsAPI = {
    async setBrands({animalId, categoryId}: GetBrandsType) {
        if (categoryId) {
            return await instance.get<Array<ResBrandType>>(`${BRANDS_URL}?animal=${animalId}&category=${categoryId}`);
        } else if(animalId) {
            return await instance.get<Array<ResBrandType>>(`${BRANDS_URL}?animal=${animalId}`);
        }
        else return await instance.get<Array<ResBrandType>>(`${BRANDS_URL}`);
    },
}