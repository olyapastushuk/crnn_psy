import React, { useState } from 'react';
import { supabase } from '../supabaseClient';
import { LogIn, UserPlus } from 'lucide-react';
import { theme } from '../theme';

const Auth = () => {
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isRegistering, setIsRegistering] = useState(false);

  const handleAuth = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      if (isRegistering) {
        const { error } = await supabase.auth.signUp({ email, password });
        if (error) throw error;
        alert('Перевірте пошту для підтвердження реєстрації!');
      } else {
        const { error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) throw error;
      }
    } catch (error) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '400px', margin: '100px auto', padding: '20px', background: theme.colors.card, borderRadius: '15px', color: 'white' }}>
      <h2 style={{ textAlign: 'center' }}>{isRegistering ? 'Реєстрація' : 'Вхід у щоденник'}</h2>
      <form onSubmit={handleAuth} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
        <input 
          type="email" placeholder="Email" value={email}
          onChange={(e) => setEmail(e.target.value)} required
          style={{ padding: '10px', borderRadius: '5px', border: 'none' }}
        />
        <input 
          type="password" placeholder="Пароль" value={password}
          onChange={(e) => setPassword(e.target.value)} required
          style={{ padding: '10px', borderRadius: '5px', border: 'none' }}
        />
        <button type="submit" disabled={loading} style={{ padding: '10px', background: theme.colors.primary, border: 'none', borderRadius: '5px', cursor: 'pointer', fontWeight: 'bold', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px' }}>
          {loading ? 'Завантаження...' : isRegistering ? <><UserPlus size={18}/> Зареєструватися</> : <><LogIn size={18}/> Увійти</>}
        </button>
      </form>
      <p onClick={() => setIsRegistering(!isRegistering)} style={{ textAlign: 'center', cursor: 'pointer', marginTop: '15px', fontSize: '14px', color: '#94a3b8' }}>
        {isRegistering ? 'Вже є аккаунт? Увійдіть' : 'Немає аккаунту? Зареєструйтеся'}
      </p>
    </div>
  );
};

export default Auth;