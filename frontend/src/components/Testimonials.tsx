const Testimonials = () => {
  const testimonials = [
    {
      name: "Daniel Garcia",
      role: "Property Manager",
      content: "Home Pulse AI makes my job as a property manager so much easier. I don't have to wonder when I need to get a project done.",
      avatar: "./profile1.jpg"
    },
    {
      name: "Amber Holup",
      role: "Real Estate Investor",
      content: "The HomeBot AI feature is a game changer. Being able to receive a forecasted replacement date has made scheduling projects so much easier.",
      avatar: "./profile3.jpg"
    },
    {
      name: "Eric Niewienski",
      role: "Property Manager",
      content: "Having a single dashboard to view all my properties is phenomenal! Managing my properties has never been easier.",
      avatar: "./profile2.jpg"
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
