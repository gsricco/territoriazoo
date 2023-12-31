import React, { useEffect, useState } from 'react';
import style from './ArticlesPage.module.scss';
import navigationStyle from '../../styles/common/NavigationBlock.module.scss';
import nextIcon from '../../Images/nextIcon.svg';
import AnimalsTypesList from '../../components/AnimalsTypesList/AnimalsTypesList';
import Article from '../../components/common/Article/Article';
import PopularProductsBlock from '../../components/PopularProductsBlock/PopularProductsBlock';
import ContactBlock from '../../components/ContactBlock/ContactBlock';
import { useDispatch, useSelector } from 'react-redux';
import { getAnimalTypes, getChosenAnimalTypeId } from '../../redux/selectors/animalTypes';
import { getArticles } from '../../redux/selectors/articles';
import { fetchArticlesTC } from '../../redux/reducers/articles';
import { useNavigate } from 'react-router-dom';
import { routesPathsEnum } from '../../routes/enums';
import { AppDispatch } from '../../redux/store';

const ArticlesPage = React.memo( () => {

  const [ showAll, setShowAll ] = useState<boolean>( false );

  const articlesFromStore = useSelector( getArticles );
  const chosenAnimalTypeId = useSelector( getChosenAnimalTypeId );
  const animalTypes = useSelector( getAnimalTypes );
  const chosenAnimalTypeName = chosenAnimalTypeId ? animalTypes.filter( type => type.id === chosenAnimalTypeId )[ 0 ].name : null;
  const articlesByAnimalTypeSorting = articlesFromStore.filter( article => article.animals === chosenAnimalTypeId );
  const getArticlesForBlock = () => {
    if ( chosenAnimalTypeId ) {
      const articles = articlesByAnimalTypeSorting;
      if ( articles.length ) {
        if ( !showAll ) {
          return articles.filter( ( article, index ) => index < 3 );
        }
        return articles;
      }
      if ( !showAll ) {
        return articlesFromStore.filter( ( article, index ) => index < 3 );
      }
      return articlesFromStore;
    }
    if ( !showAll ) {
      return articlesFromStore.filter( ( article, index ) => index < 3 );
    }
    return articlesFromStore;
  };
  const articles = getArticlesForBlock();

  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();

  useEffect( () => {
    const chosenAnimalId = chosenAnimalTypeId ? chosenAnimalTypeId : null
    dispatch( fetchArticlesTC( { chosenAnimalId } ) );
  }, [ dispatch, chosenAnimalTypeId ] );

  return (
    <div className={ style.articlesPageBlock }>
      <div className={ navigationStyle.navigationBlock }>
        <div className={ navigationStyle.navigationBlockWrapper }>
          <p onClick={ () => navigate( routesPathsEnum.MAIN ) }>Главная</p>
          <img src={ nextIcon } loading={ 'lazy' } alt="nextIcon" draggable="false"/>
          <p>Статьи</p>
        </div>
      </div>
      <AnimalsTypesList/>
      <div className={ style.articlesTitle }>
        <h2>{ chosenAnimalTypeName ? `${ chosenAnimalTypeName } - полезные статьи` : 'Полезные статьи' }</h2>
      </div>
      <div className={ style.articlesBlockContainer }>
        <div className={ style.articlesBlock }>
          {
            articles.map( ( { id, title, description, time_read, date_added, image } ) =>
              <Article
                key={ id }
                id={ id }
                title={ title }
                description={ description }
                timeForReading={ time_read }
                date_added={ date_added }
                image={ image }
                forArticlesPage={ true }
              />,
            )
          }
        </div>
        { !showAll && articlesByAnimalTypeSorting.length < 3 &&
          <button onClick={ () => setShowAll( true ) }>Показать ещё</button> }
      </div>
      <PopularProductsBlock fromCatalog={ false }/>
      <ContactBlock/>
    </div>
  );
} );

export default ArticlesPage;