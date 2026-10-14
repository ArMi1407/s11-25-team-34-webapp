import { Title } from '../../atoms/text/Title';
import logo from '../../../assets/icons/logo.png';

export const Brand = () => {
  return (
    <div className="flex items-center gap-2">
      <img src={logo} alt="Brand Logo" style={{ width: 26, height: 28 }} />
      <Title variant="subtitle" className="text-primary text-3xl">
        EcoBeauty
      </Title>
    </div>
  );
};
