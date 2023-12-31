import React, { ReactElement } from 'react';
import Address from '../../common/Address/Address';
import Phone from '../../common/PhoneBlock/Phone';
import Schedule from '../../common/Schedule/Schedule';
import Callback from '../../common/Callback/Callback';
import style from './FooterBurger.module.scss';
import { useSelector } from 'react-redux';
import { getInfo } from '../../../redux/selectors/descriptionShop';

const FooterBurger = React.memo((): ReactElement => {
  const { address, metro, time_weekdays, time_weekend, phone_number } = useSelector( getInfo );
  return (
    <footer className={ style.footerBurger }>
      <Address address={ address } metro={ metro } forBurger={true}/>
      <div className={ style.instaBlock }>
        <Phone phoneNumber={ phone_number }/>
        <div className={ style.instagramIcon }/>
      </div>
      <Schedule forFooterBurger={ true } timeWeekdays={ time_weekdays } timeWeekend={ time_weekend }/>
      <Callback forHeader={ false }/>
    </footer>
  );
});

export default FooterBurger;