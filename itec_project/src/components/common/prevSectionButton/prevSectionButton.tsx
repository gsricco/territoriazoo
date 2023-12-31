import React, { ReactElement } from 'react';
import style from './prevSectionButton.module.scss';
import { SectionButtonPropsType } from '../types';

const PrevSectionButton = ( { onClick, disabled }: SectionButtonPropsType ): ReactElement => {
  return (
    <button
      className={ disabled ? `${ style.button } ${ style.disabledButton }` : style.button }
      onClick={ onClick }
      disabled={ disabled }
      aria-label={ 'previousSection' }
    />
  );
};

export default PrevSectionButton;