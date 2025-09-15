const Testimonials = () => {
  const testimonials = [
    {
      name: "Sarah Johnson",
      role: "First-time Homebuyer",
      content: "RealEstate Pro made finding my dream home so easy. The search tools are incredible and the team was supportive throughout the entire process.",
      avatar: "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=100&h=100&fit=crop&crop=face"
    },
    {
      name: "Michael Chen",
      role: "Real Estate Investor",
      content: "The market analytics feature is a game-changer. I've been able to identify profitable investment opportunities that I would have missed otherwise.",
      avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face"
    },
    {
      name: "Emily Rodriguez",
      role: "Property Seller",
      content: "Sold my house in just 2 weeks! The platform's reach and the professional support made all the difference in getting the best price.",
      avatar: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&h=100&fit=crop&crop=face"
    }
  ];

  return (
    <section id="testimonials" className="py-20 px-4 relative z-10">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            What Our Clients Say
          </h2>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            Hear from satisfied customers who found their perfect properties with us
          </p>
        </div>

        <div className="space-y-16">
          {testimonials.map((testimonial, index) => (
            <div key={index} className="max-w-4xl mx-auto">
              <div className="bg-white/5 backdrop-blur-md rounded-2xl p-8 md:p-12 border border-white/10">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-center">
                  <div className="lg:col-span-1 text-center lg:text-left">
                    <div className="inline-block p-1 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full mb-4">
                      <img
                        src={testimonial.avatar}
                        alt={testimonial.name}
                        className="w-24 h-24 rounded-full object-cover"
                      />
                    </div>
                    <h3 className="text-2xl font-bold text-white mb-2">{testimonial.name}</h3>
                    <p className="text-blue-300 font-medium">{testimonial.role}</p>
                  </div>
                  <div className="lg:col-span-2">
                    <blockquote className="text-xl md:text-2xl text-gray-200 italic leading-relaxed">
                      "{testimonial.content}"
                    </blockquote>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Testimonials;
