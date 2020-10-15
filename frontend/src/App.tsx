import React from 'react';
import './App.css';

import { gql, useQuery } from '@apollo/client';

const GET_CONNECTION = gql`
{connection (id: 1) { name actions { due }}}
`;

function App() {

  const { loading, error, data } = useQuery(GET_CONNECTION, {
    variables: {id: 1}
  })
  return (
    <div className="App">
      <p>Hi</p>
    </div>
  );
}

export default App;
