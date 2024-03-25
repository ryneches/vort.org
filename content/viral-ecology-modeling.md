#### Modeling the viral ecology of a simple bacterial culture

[David Demory](https://github.com/DDemory) is visiting our laboratory from The Laboratory of Microbial Biodiversity
and Biotechnology ([LBBM](https://usr3579.obs-banyuls.fr/en/index.html)) for a few weeks, and yesterday he led a great workshop on modeling for us. David used to be a postdoc in my friend [Joshua Weitz's group](https://weitzgroup.umd.edu/people/) when he was at Georgia Tech, a leader of theoretical modeling in virology and a great advocate for the power of theory in biology generally. David mostly works in [Julia](https://julialang.org/), but for teaching purposes he used R, because there are several R users in our group.

While I have a lot of respect for R as a community and giant pile of important software implemented in R, I've always more comfortable working in Python. [It's been a long time](https://doi.org/10.1063/1.3008049) since I've needed to do numerical integration, and it turns out that in things have changed a bit since I last reached for `scipy.integrate`, and things have changed a lot! [It's been seven years](https://github.com/scipy/scipy/commit/5ec790f8a975483784a96affa34cf61025936aa7) since `solve_ivp` was first committed to the codebase, but most of the easily discoverable examples in the web and answers on StackOverflow are still using the old framework, and the examples using `solve_ivp` that I could find either illustrate trivial cases, or the explanations are very terse. Neither are much help to a person who isn't already very experienced with numerical computing in Python. With his blessing, I've developed the problems from David's workshop using scipy's "new" ODE solver, [`solve_ivp`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html).

This article covers the following :

* What do we mean by "model" in the first place?
* Expressing a model as a system of ordinary differential equations in Python
* Setting model parameters and boundary conditions
* Solving the model numerically by direct integration
* Plotting variables and phase planes
* Exploring the model with interactive controls in Jupyter

#### Describing a model

We are going to look at the population dynamics of viruses and their hosts. To start with, we're going to use a model that is much simpler than what you'd [typically find in epidemiology](https://en.wikipedia.org/wiki/Compartmental_models_in_epidemiology). In this model, every infection immediately kills the host and releases a burst of new virions. This is basically the [Lotka-Volterra predator-prey model](https://en.wikipedia.org/w/index.php?title=Lotka%E2%80%93Volterra_equations), modified to include add a carrying capacity instead of allowing the host to grow exponentially. Where $S$ is the population of susceptible hosts (cells per milliliter) and $V$ is the population of viruses (virions per milliliter), we get the following model :


$$\frac{dS}{dt} = \underbrace{\mu S \left[ 1 - \frac{S}{K}\right]}_{\text{logistical growth}} - \underbrace{ \vphantom{\left(\frac{S}{K}\right)} \psi S }_{\mathclap{\text{natural death}}} - \underbrace{ \vphantom{\left(\frac{S}{K}\right)} \phi S V }_{\mathclap{\text{lysis}}} $$
$$\frac{dV}{dt} = \underbrace{ \beta \phi S V }_{\text{release}} - \underbrace{ \vphantom{\beta} \delta V }_{\text{decay}} $$
**Variables**
* $S$ : host population
* $V$ : virion population

**Parameters**
* $\phi$ : viral infection rate ($\frac{\text{mL}}{\text{hour} \times \text{cells}}$)
* $\delta$ : viral decay rate ($\text{hour}^{-1}$)
* $\psi$ : host mortality ($\text{hour}^{-1}$)
* $\mu$ : host growth rate ($\text{hour}^{-1}$)
* $K$ : carrying capacity ($\text{cells} \times \text{mL}^{-1}$)
* $\beta$ : virion production by lysis ($\text{virions} \times \text{cell}^{-1}$ )

**Initial conditions**
* $S_0$ : initial host population
* $V_0$ : initial virion population
* $t_0$ : start time
* $t_1$ : end time

This is the definition of our model. If you like, it is possible to solve it analytically, particularly for boundary cases. For example, if you start without any viruses by setting $V_0=0$, or you start with the host population already at carrying capacity $S_0=K$, you can learn discover the important features of the model just with pencil and paper. But, if we dive into that topic, this will become a math class. So, let's build it our model in Python. We'll start by importing our modules.

#### Expressing the model in Python

    :::python
    import matplotlib.pyplot as plt
    import numpy as np, exp
    from scipy.integrate import solve_ivp

Next, let's express the SV model as a Python function. This function must be constructed in the following way :
* It must have at least two arguments (`f(t, y)`)
* The first argument (`t`) is the independent variable, and must be a scalar
* The second argument (`y`) must be an array of the dependent variables
* It must must return an array of the same shape as y

There are two ways to pass your parameters into this function. The easy way is to just define them in the calling scope, like so :

    :::python
    # model
    a = 12.345
    def f( t, y ) :
       return a * y

This is fine if you are just tinkering around, but I encourage you to think of this as a "naughty" practice. Especially in a notebook environment, it's very easy to set a variable and then forget about it when you re-write the code cell. The notebook kernel remembers the value you set even if you delete the code cell that set the parameter. It can be very confusing to debug.

It's better practice to set parameters as arguments after `y`, like so :

    :::python
    # model
    def f( t, y, a ) :
        return a * y

The order of the parameters after `y` is important! They will be passed into the model function by `solve_ivp` from a list.

In our case, time dependence is only on the left side of the system equations, and so `t` is not used in the function itself. The SV system looks like this :

    :::python
    # model
    def SV( t, y, phi, delta, psi, mu, K, beta ) :
       s, v = y
       ds = mu * s * ( 1 - s/K ) - psi * s - phi * s * v
       dv = beta * phi * s * v - delta * v
       
       return ( ds, dv )

#### Model parameters and boundary conditions

Now, we need to choose some values for our parameters, initial conditions, and discretize our independent variable. These values were selected by David for his workshop.

    :::python
    # model parameters
    phi   = 6e-10  # viral infection rate
    delta = 1/24   # viral decay rate
    psi   = 1/4    # host mortality
    mu    = 0.95   # host growth rate
    K     = 7.5e7  # carrying capacity
    beta  = 50     # virion burst size

    # initial conditions
    t0 = 0    # initial time
    t1 = 1680 # one academic quarter
    s0 = 1000 # initial host population
    v0 = 1000 # initial virus population

    # solution domain
    t_eval = np.arange( t0, t1, 0.01 )

#### Solving the model by numerical integration

That's all the setup done, so let's solve the system. The `solve_ivp` function takes three positional arguments : the model function, the initial and ending value of the independent variable, and an array of the initial values for the system variables. The initial values should be in the same order they appear in the model function.

If you are passing your parameters in explicitly (as I recommend), the `args` argument takes a list, tuple or array with the parameters in the same order they appear in the model function. You can let the solver chop up the interval for the independent variable itself, but I suggest you also pass in the values you want with `t_eval`.

Last of all, you can select the integration approach using the `method` argument. [The documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html) lists the options, but the default is `RK45`, one of the [Runge-Kutta](https://en.wikipedia.org/wiki/Runge%E2%80%93Kutta_methods) methods. You may have learned a version of it in high school calculus, where you cut the function into half-trapezoid strips to add up the area under the curve. Probably, the default will be fine for most applications.

    :::python
    # solution
    sol = solve_ivp( SV, 
        [t0, t1],
        [s0, v0],
        args=( phi, delta, psi, mu, K, beta ),
        t_eval=t_eval,
        method='RK45' )

The solution object has a bunch of interesting stuff in it it, but we're mostly interested in `t` and `y`. 

    :::python
    message: The solver successfully reached the end of the integration interval.
    success: True
    status: 0
            t: [ 0.000e+00  1.000e-02 ...  1.680e+03  1.680e+03]
            y: [[ 1.000e+03  1.007e+03 ...  1.412e+06  1.412e+06]
                [ 1.000e+03  9.996e+02 ...  1.135e+09  1.135e+09]]
        sol: None
    t_events: None
    y_events: None
        nfev: 1596
        njev: 26
        nlu: 26

If your want to find roots, or parts of the phase plane where other conditions are satisfied, you can define them as functions and pass them to `solve_ivp` using the `events` argument, and the solutions will be in `t_events` or `y_events`. It's a very powerful and flexible interface! See the documentation for more about that.

#### Plotting the model

Let's make two plots. The first will show the $S(t)$ and $V(t)$ by plotting `y[0]` and `y[1]` verses `t`. This is the time evolution of the system. In the second, we'll show a parametric plot of $x=S(t)$ and $y=V(t)$. This is the phase plane of system.

    :::python
    plt.figure(figsize = (8, 4))
    plt.subplot(121)
    plt.plot(sol.t, sol.y[0], label='host')
    plt.plot(sol.t, sol.y[1], label='virus')
    plt.title( 'population history' )
    plt.semilogy()
    plt.xlabel('hours')
    plt.ylabel('population')
    plt.legend()
    plt.subplot(122)
    plt.plot(sol.y[0], sol.y[1] )
    plt.title( 'phase plane' )
    plt.loglog()
    plt.xlabel('cells')
    plt.ylabel('virions')
    plt.tight_layout()

![assets/sv_model.png]

OK! It looks like everything works! I happened to choose parameters that put the system into an interesting state. 

#### Expanding the model

I find that it's really helpful to compare and contrast two similar applications of a tool to really understand how it works. So, let's expand our model a little bit. Instead of treating infection and lysis as an instantaneous event, let's add a new variable to the system to represent infected cells. In this model, there's no recovery, so infection always results in lysis. Both susceptible and infected cells can also die "normally."

$$\frac{dS}{dt} = \mu S\left( 1 - \frac{S+I}{K}\right) - \psi S -\phi S V $$
$$\frac{dI}{dt} = \phi S V - \eta I - \psi I $$
$$\frac{dV}{dt} = \eta \beta I - \delta V - \phi S V$$
The system now has three differential equations, one new variable $I$ to represent infected cells, and one new parameter $\eta$ to represent the what fraction of infected cells lyse per hour. We've also got one more initial condition $I_0$ for the number of infected cells to start out with.

**Variables**
* $S$ : susceptible host population
* $I$ : infected host population
* $V$ : virion population

**Parameters**
* $\phi$ : viral infection rate ($\frac{\text{mL}}{\text{hour} \times \text{cells}}$)
* $\delta$ : viral decay rate ($\text{hour}^{-1}$)
* $\psi$ : host mortality ($\text{hour}^{-1}$)
* $\mu$ : host growth rate ($\text{hour}^{-1}$)
* $K$ : carrying capacity ($\text{cells} \times \text{mL}^{-1}$)
* $\beta$ : virion production by lysis ($\text{virions} \times \text{cell}^{-1}$ )
* $\eta$  : lytic rate ($\text{hour}^{-1}$)

**Initial conditions**
* $S_0$ : initial susceptible host population
* $I_0$ : initial infected host population
* $V_0$ : initial virion population
* $t_0$ : start time
* $t_1$ : end time

The model function has the same variable arguments `t` and `y` and one additional parameter, `eta`. However, `y` now has a length of three, corresponding to the three differential equations. The function must now also return three values.

    :::python
    # model
    def SIV( t, y, phi, delta, psi, mu, K, beta, eta ) :
        s, i, v = y
        ds = mu  * s * ( 1 - (s+i)/K ) - psi * s - phi * s * v
        di = phi * s * v               - eta * i - psi * i
        dv = eta * beta * i - delta * v - phi * s * v
        
        return ( ds, di, dv )

We'll set the parameters like before, except this time we also have `eta` and `i0`. Note also that this time I'm starting the host population off at the carrying capacity $K$.

    :::python
    # model parameters
    phi   = 6.7e-10 # viral infection rate
    delta = 1/24    # viral decay rate
    psi   = 1/4     # host mortality rate
    mu    = 0.95    # host growth rate
    K     = 7.5e7   # carrying capacity
    eta   = 0.5     # lytic rate
    beta  = 50      # burst size

    # initial conditions
    t0 = 0
    t1 = 1680 # one academic quarter
    s0 = K
    v0 = 100
    i0 = 0

    # solution domain
    t_eval = np.arange( t0, t1, 0.01 )

To solve, we also have to start the simulation with the initial values for $I$ as `i0` and pass the parameter `eta` to the model function. 

    :::python
    # solution
    sol = solve_ivp( SIV, 
                    [t0, t1],
                    [s0,i0,v0],
                    args=( phi, delta, psi, mu, K, beta, eta ),
                    t_eval=t_eval,
                    method='RK45' )

Now, we plot like before. This time, let's also add a dashed line so we can see what the system carrying capacity is.

    :::python
    plt.figure(figsize = (8, 4))
    plt.subplot(121)
    plt.plot(sol.t, sol.y[0], label='host')
    plt.plot(sol.t, sol.y[1], label='virus')
    plt.axhline( K, color='black', linestyle=':' )
    plt.title( 'population history' )
    plt.semilogy()
    plt.xlabel('hours')
    plt.ylabel('population')
    plt.legend()
    plt.subplot(122)
    plt.plot(sol.y[0], sol.y[1] )
    plt.title( 'phase plane' )
    plt.loglog()
    plt.xlabel('cells')
    plt.ylabel('virions')
    plt.tight_layout()

![assets/siv_model.png]


Let's have a look at $R_0$, the [basic reproduction number](https://en.wikipedia.org/wiki/Basic_reproduction_number). $R_0$ is the expected number of new infections generated by each infection. In a real epidemic it would usually be estimated by observation to infer the other parameters. However, in our model, we can work it out algebraically from the parameters :

$$ R_0 = \beta \frac{\eta}{\eta+\psi} \frac{\phi S^*}{\phi S^* + \delta}$$where $S^*=K \frac{\mu - \psi}{\mu}$. In order for an virus to spread, $R_0$ must be greater than one. SARS-CoV-2 had an $R_0$ of [around 2.9 at the beginning of the outbreak, and then climbed to more than 9](https://doi.org/10.1093%2Fjtm%2Ftaac037) as the virus adapted to reproduction in humans. Measles has an $R_0$ somewhere around 12 to 18, which makes it an absolute monster. However, a virus's $R_0$ can be pushed below 1 for a sustained period, it can be driven to complete extinction, as was accomplished with Smallpox in 1980.

Let's use $R_0$$ to help pick some new model parameters. We'll make a function that takes all of our parameters as defaults from the calling context, like so : 

    :::python
    def R0( phi=phi, delta=delta, psi=psi, beta=beta, eta=eta ) :
        S = K * ( ( mu - psi ) / mu )
        return beta * ( eta / ( eta + psi ) ) * ( ( phi * S ) / ( phi * S + delta ) )

Now, we can conveniently calculate how $R_0$ responds to varying any of the model parameters. As long as the parameters we just used are still in the calling context, we can do this :

    :::python
    B = range( 1, 100 )
    R = [ R0(beta=b) for b in B ]

    plt.plot( B, R )
    plt.axhline( 1.0, linestyle=':' )
    plt.xlabel( r'$\beta$' )
    plt.ylabel( r'$R_0$' )

![assets/r0_vs_beta.png]

It looks like the threshold for $\beta$ that gives us $R_0>1$ is about 25. Let's nail that down more precisely with `fsolve` :

    :::python
    from scipy.optimize import fsolve

    fsolve( lambda b : R0( beta=b ) - 1, [0,100] )

This gives us the result :

    :::python
    array([26.81982942, 26.81982942])

If we re-run the numerical solution with $\beta = 26.81982942$, the model is poised right at the critical threshold. Looking at the population plots, the virus doesn't appear to be growing, but isn't going extinct either, hovering at less than one virion per milliliter of culture. However, if we look at the phase plane, it looks like the virus is indeed heading very slowly toward extinction. 

![assets/siv_model_critical_r0.png]

Let's try this for $\eta$, the lysis rate, which is inversely proportional to the incubation period. 

    :::python
    E = np.arange( 0.01, 1.0, 0.01 )
    R = [ R0(eta=e) for e in E ]

    plt.plot( E, R )
    plt.axhline( 1.0, linestyle=':' )
    plt.xlabel( r'$\eta$' )
    plt.ylabel( r'$R_0$' )

![assets/r0_vs_lysis.png]

This time, we have a nonlinear relationship between $\eta$ and $R_0$, but we can still find the critical value the same way :

    :::python
    fsolve( lambda e : R0( eta=e ) - 1, [0,1.0] )

    array([0.5504814, 0.5504814])

#### Interactive exploration in Jupyter

It's very easy to try out different model parameters this way, but it's still a little bit cumbersome to explore the parameters space. Fortunately, there is a set of interactive browser controls called [Jupyter Widgets](https://ipywidgets.readthedocs.io/en/latest/). This makes it possible to connect our parameters to widgets like buttons, sliders, selection boxes and checkboxes, and then re-run our model and replot the results when you adjust a parameter. The model runs fast enough on modern computers that this can produce a live view of the results as you drag the slider back and forth! It's a very powerful way to gain an intuitive understanding of how each parameter affects the model and how they interact.

To use Jupyter Widgets, make sure the package `ipywidgets` is [installed](https://ipywidgets.readthedocs.io/en/latest/user_install.html) (the Jupyter project used to be called IPython, if you're wondering what's up with the name). Then import some things from it :

    :::python
    from ipywidgets import interactive, widgets, Layout, HBox, VBox

Then, we just take the model code we've been using, and wrap it in a function that runs the model and makes the plots :

    :::python
    def makeplot( s0, v0, phi, delta, psi, mu, K, beta, eta, t1 ) :

        # model
        def SIV( t, y, phi, delta, psi, mu, K, beta, eta ) :
            s, i, v = y
            ds = mu  * s * ( 1 - (s+i)/K ) - psi * s - phi * s * v
            di = phi * s * v               - eta * i - psi * i
            dv = eta * beta * i - delta * v - phi * s * v
        
            return ( ds, di, dv )
            
        # solution domain
        t_eval = np.arange( t0, t1, 1.0 )
        
        # solution
        sol = solve_ivp( SIV, 
                        [t0, t1],
                        [s0,i0,v0],
                        args=( phi, delta, psi, mu, K, beta, eta ),
                        t_eval=t_eval,
                        method='LSODA' )

        plt.figure(figsize = (8, 4))
        plt.subplot(121)
        plt.plot(sol.t, sol.y[0], label='host')
        plt.plot(sol.t, sol.y[1], label='virus')
        plt.axhline( K, color='black', linestyle=':' )
        plt.title( 'population history' )
        plt.semilogy()
        plt.xlabel('hours')
        plt.ylabel('population')
        plt.legend()
        plt.subplot(122)
        plt.plot(sol.y[0], sol.y[1] )
        plt.title( 'phase plane' )
        plt.loglog()
        plt.xlabel('S')
        plt.ylabel('V')
        plt.tight_layout()

There are somewhat simpler ways to use Jupyter Widgets that dispense with some of the code I'm about to show you, but we have a lot of sensitive parameters. Usually, I think you will want to explicitly set the starting values and the ranges of each parameter. So, for each parameter we want to play with, we create a `FloatSlider` object configured with the default values, minimums and maximums. For parameters like $K$ and $\phi$ which will tend to have very large or very small values, we also set `readout_format` to display the number in scientific notation.

    :::python
    # model parameters
    phi_0   = 6.7e-10 # viral infection rate
    delta_0 = 1/24    # viral decay rate
    psi_0   = 1/4     # host mortality rate
    mu_0    = 0.95    # host growth rate
    K_0     = 7.5e7   # carrying capacity
    eta_0   = 0.5     # lytic rate
    beta_0  = 50      # burst size

    # initial conditions
    t0 = 0
    t1_0 = 1680 # one academic quarter
    s0 = K
    v0 = 100
    i0 = 0

    v0_w    = widgets.FloatSlider( min=0, max=1000, step=1, value=v0,
                                orientation='vertical', description=r'$V_0$' )
    s0_w    = widgets.FloatSlider( min=1, max=1000, step=1, value=s0,
                                orientation='vertical', description=r'$S_0$' )
    phi_w   = widgets.FloatSlider( min=0, max=2e-9, step=1e-12, value=phi_0,
                                orientation='vertical', description=r'$\phi$',
                                readout_format='.2e' )
    delta_w = widgets.FloatSlider( min=0, max=1, step=0.01, value=delta_0,
                                orientation='vertical', description=r'$\delta$' )
    psi_w   = widgets.FloatSlider( min=0, max=1, step=0.01, value=psi_0,
                                orientation='vertical', description=r'$\psi$' )
    K_w     = widgets.FloatSlider( min=0, max=2e8, step=0.01, value=K_0,
                                orientation='vertical', description=r'$K$',
                                readout_format='.2e' )
    mu_w    = widgets.FloatSlider( min=0, max=2, step=0.01, value=mu_0,
                                orientation='vertical', description=r'$\mu$' )
    beta_w  = widgets.FloatSlider( min=0, max=100, step=1, value=beta_0,
                                orientation='vertical', description=r'$\beta$' )
    eta_w   = widgets.FloatSlider( min=0.0, max=1.0, step=0.01, value=eta_0,
                                orientation='vertical', description=r'$\eta$' )
    t1_w    = widgets.FloatSlider( min=1, max=2000, step=1, value=t1_0,
                                orientation='vertical', description=r'$t_1$' )


Next, we build the interactive widget by binding each of `FloatSlider` to its corresponding parameter in the function that wraps our modeling and plotting code :

    :::python
    widget = interactive( makeplot,
                        v0=v0_w,
                        s0=s0_w,
                        phi=phi_w,
                        delta=delta_w,
                        psi=psi_w,
                        mu=mu_w,
                        K=K_w,
                        beta=beta_w,
                        eta=eta_w,
                        t1=t1_w )

This would actually be enough! If you call `interactive()` directly, Jupyter will display the results just fine. The problem is that the layout of the `FloatSlider` widgets will be ugly. So, let's wrap the controls in `HBox` that has a flow wrap layout. This way, each control will be added left to right, the same way that letters text flow in English text. Then, we wrap the `HBox` with our controls and the plot output in a `VBox` so they'll be stacked nicely on top of each other.

    :::python
    controls = HBox( widget.children[:-1],
                                    layout = Layout( flex_flow = 'row wrap' ) )
    output = widget.children[-1]
    display( VBox( [ controls, output ] ) )

Now, we can play around with the sliders, and the model will automatically run and update the plot! It does not take very long to quickly develop a sense for what role each parameter plays in the system when you can see the results immediately.

![assets/siv_ipywidgets.png]

The numerical integration methods are extremely good at fitting smooth curves, so it isn't necessary to use extremely fine discretization to get reasonably accurate results. I found that it is possible to use a very course step size to get essentially instant live feedback!

Once again, I'd like to thank David for coming to visit us, and for taking the time to put together this fantastic workshop just for us.
