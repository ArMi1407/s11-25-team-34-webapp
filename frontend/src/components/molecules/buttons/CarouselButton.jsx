// molecules/ControlsMolecule.jsx
import { Button } from '../../atoms/button/Button';
import { IoChevronBack, IoChevronForward } from 'react-icons/io5';

export const CarouselButton = ({ onPrev, onNext }) => (
  <div className="absolute inset-0 flex items-center justify-between px-2 md:px-4">
    <Button
      variant="ghost"
      icon={IoChevronBack}
      onClick={onPrev}
      className=" backdrop-blur-md p-2 rounded-full"
      iconClassName="w-6 h-6 text-white"
    />

    <Button
      variant="ghost"
      icon={IoChevronForward}
      onClick={onNext}
      className="backdrop-blur-md p-2 rounded-full"
      iconClassName="w-6 h-6 text-white"
    />
  </div>
);
