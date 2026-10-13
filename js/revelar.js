const obs=new IntersectionObserver((secoes) =>{
    secoes.forEach(secao =>{
        if(secao.isIntersecting){
            secao.target.classList.add('visivel')
            obs.unobserve(secao.target)
        }
    })
}, {threshold: 0.1})
document.querySelectorAll('.revelar').forEach(el => obs.observe(el))