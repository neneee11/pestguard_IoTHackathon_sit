import { RegisterForm } from '@/component/RegisterForm';
import { BookingPage } from '@/component/BookingPage';
import { ConfirmationPage } from '@/component/ConfirmationPage';
import { SuccessPage } from '@/component/SuccessPage';
import { useAppStore } from '@/stores/appStore';

const Index = () => {
  const { currentStep } = useAppStore();

  return (
    <>
      {currentStep === 'register' && <RegisterForm />}
      {currentStep === 'booking' && <BookingPage />}
      {currentStep === 'confirm' && <ConfirmationPage />}
      {currentStep === 'success' && <SuccessPage />}
    </>
  );
};

export default Index;
