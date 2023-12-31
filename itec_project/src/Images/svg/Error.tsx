import React, { SVGProps } from 'react';

const Error = ( props: SVGProps<SVGSVGElement> ) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 48 48"
    width={ 40 }
    height={ 40 }
    { ...props }
  >
    <path
      fill="#f44336"
      d="M44 24c0 11.045-8.955 20-20 20S4 35.045 4 24 12.955 4 24 4s20 8.955 20 20z"
    />
    <path
      fill="#fff"
      d="m29.656 15.516 2.828 2.828-14.14 14.14-2.828-2.828 14.14-14.14z"
    />
    <path
      fill="#fff"
      d="m32.484 29.656-2.828 2.828-14.14-14.14 2.828-2.828 14.14 14.14z"
    />
  </svg>
);

export default Error;