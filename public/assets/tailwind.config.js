tailwind.config = {
            theme: {
                extend: {
                    fontFamily: { sans: ['Plus Jakarta Sans', 'system-ui', 'sans-serif'] },
                    colors: {
                        brand: {
                            50: '#F0F4FA',
                            100: '#DCE6F5',
                            200: '#B8CCE9',
                            300: '#8AABD8',
                            400: '#5283C2',
                            500: '#1D5FC6',
                            600: '#0A3882',
                            700: '#002B66',
                            800: '#00204D',
                            900: '#001433'
                        },
                        cardio: {
                            50: '#FFF0F3',
                            100: '#FFE0E6',
                            200: '#FFC2CD',
                            300: '#FF94A8',
                            400: '#FF5C7E',
                            500: '#E4003B',
                            600: '#CC0035',
                            700: '#A3002A',
                            800: '#7A001F',
                            900: '#520015'
                        },
                        clinical: {
                            success: '#059669',
                            warning: '#D97706',
                            danger: '#DC2626',
                            info: '#2563EB'
                        }
                    },
                    animation: {
                        'fade-in': 'fadeIn 0.25s ease-out',
                        'slide-up': 'slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1)'
                    },
                    keyframes: {
                        fadeIn: { from: { opacity: '0' }, to: { opacity: '1' } },
                        slideUp: { from: { opacity: '0', transform: 'translateY(10px)' }, to: { opacity: '1', transform: 'translateY(0)' } }
                    }
                }
            }
        }
