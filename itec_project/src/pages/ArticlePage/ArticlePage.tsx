import React, { useEffect } from 'react';
import UsefulArticlesBlock from '../../components/UsefulArticlesBlock/UsefulArticlesBlock';
import PopularProductsBlock from '../../components/PopularProductsBlock/PopularProductsBlock';
import ContactBlock from '../../components/ContactBlock/ContactBlock';
import { useNavigate, useParams } from 'react-router-dom';
import style from './ArticlePage.module.scss';
import navigationStyle from '../../styles/common/NavigationBlock.module.scss';
import nextIcon from '../../Images/nextIcon.svg';
import colorTimeIcon from '../../Images/colorTimeIcon.svg';
import colorCalendarIcon from '../../Images/colorCalendarIcon.svg';
import commonStyle from '../../styles/common/Container.module.scss';
import { useDispatch, useSelector } from 'react-redux';
import { getArticles } from '../../redux/selectors/articles';
import { routesPathsEnum } from '../../routes/enums';
import { getCurrentAddedDate } from '../../helpers/getDate';
import { AppDispatch } from '../../redux/store';
import { fetchArticleTC } from '../../redux/reducers/article';

const ArticlePage = React.memo( () => {
  const articleId = Number( useParams().articleId ) - 1;
  const article = useSelector( getArticles )[ articleId ];
  const date = new Date( article.date_added );
  const currentData = getCurrentAddedDate( date );
  const navigate = useNavigate();
  const dispatch = useDispatch<AppDispatch>();
  useEffect( () => {
    dispatch( fetchArticleTC( { id: articleId } ) );
  }, [] );

  return (
    <div className={ style.articlePage }>
      <div className={ commonStyle.container }>
        <div className={ navigationStyle.navigationBlock }>
          <div className={ navigationStyle.navigationBlockWrapper }>
            <p onClick={ () => navigate( routesPathsEnum.MAIN ) }>Главная</p>
            <img src={ nextIcon } loading={ 'lazy' } alt="nextIcon" draggable="false"/>
            <p onClick={ () => navigate( routesPathsEnum.ARTICLES ) }>Статьи</p>
            <img src={ nextIcon } loading={ 'lazy' } alt="nextIcon" draggable="false"/>
            <p>{ article.title }</p>
          </div>
        </div>
        <div className={ style.articleTitle }>
          <h1>{ article.title }</h1>
        </div>
        <div className={ style.articleInfo }>
          <div className={ style.articleReadingWrapper }>
            <div>
              <img src={ colorTimeIcon } loading={ 'lazy' } alt="timeIcon"/>
              <p>Время чтения: { article.time_read }</p>
            </div>
            <div>
              <img src={ colorCalendarIcon } loading={ 'lazy' } alt="calendar"/>
              <p>{ currentData }</p>
            </div>
          </div>
        </div>
        <div className={ style.articleImage }>
          <img src={ article.image } loading={ 'lazy' } alt="article"/>
        </div>
        <div className={ style.articleTextContainer }>
          <p className={ style.articleText }
             dangerouslySetInnerHTML={ { __html: article.description } }/>
        </div>
      </div>
      <UsefulArticlesBlock/>
      <PopularProductsBlock fromCatalog={ false }/>
      <ContactBlock/>
    </div>
  );
} );

export default ArticlePage;