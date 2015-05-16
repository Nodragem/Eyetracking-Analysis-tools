__author__ = 'c1248317'

def getDensityOneType_scipy(halfdist, tab, select_type, x_range, bw="scott"):

    selection_end = (tab.trial_type == select_type ) &(tab.marker == 2) & selectByHalfDistance(tab, halfdist)
    selection_start = (tab.trial_type == select_type ) &(tab.marker == 1) & selectByHalfDistance(tab, halfdist)
    data_driftcorrected = tab.ix[selection_end, ["xp","yp"]].values[:]\
                        - tab.ix[selection_start, ["xp","yp"]].values[:]

    target_dir = tab.ix[selection_end, ["target_dir"]].values[:]
    ## let's just take Y-axis:
    data_mirroted = mirrorConditions(target_dir, data_driftcorrected)[:,1]

    kde = sc.gaussian_kde(data_mirroted, bw_method = bw) ## condition control
    density = kde(x_range)

    return density, kde.factor, data_mirroted.mean(), data_mirroted.std()


def getDensityOneType(halfdist, tab, select_type, x_range):

    selection_end = (tab.trial_type == select_type ) &(tab.marker == 2) & selectByHalfDistance(tab, halfdist)
    selection_start = (tab.trial_type == select_type ) &(tab.marker == 1) & selectByHalfDistance(tab, halfdist)
    data_driftcorrected = tab.ix[selection_end, ["xp","yp"]].values[:]\
                        - tab.ix[selection_start, ["xp","yp"]].values[:]

    target_dir = tab.ix[selection_end, ["target_dir"]].values[:]
    ## let's just take Y-axis:
    data_mirroted = mirrorConditions(target_dir, data_driftcorrected)[:,1]

    grid = GridSearchCV( sk.KernelDensity(),{'bandwidth': np.linspace(1.0, 200.0, 30)},cv=20 )
    grid.fit(data_mirroted[:, np.newaxis])
    kde = grid.best_estimator_ ## condition control
    density = np.exp(kde.score_samples(x_range[:, np.newaxis]))

    return density, data_mirroted.mean(), data_mirroted.std()

def createBimodalModel(halfdist, tab, x_range, p):

    selection_end = (tab.marker == 2) & selectByHalfDistance(tab, halfdist)
    selection_start = (tab.marker == 1) & selectByHalfDistance(tab, halfdist)

    data_driftcorrected = tab.ix[selection_end, ["xp","yp"]].values[:]\
                        - tab.ix[selection_start, ["xp","yp"]].values[:]

    target_dir = tab.ix[selection_end, ["target_dir"]].values[:]
    c = tab.ix[selection_end, ["trial_type"]].values[:]
    c = c.reshape(len(c))

    ## let's just take Y-axis:
    data_mirroted = mirrorConditions(target_dir, data_driftcorrected)[:,1]

    model_target = data_mirroted[c==1]
    grid = GridSearchCV( sk.KernelDensity(),{'bandwidth': np.linspace(1.0, 200.0, 30)},cv=20 )
    grid.fit(model_target[:, np.newaxis])
    kde_target = grid.best_estimator_ ## condition control
    density_target = np.exp(kde_target.score_samples(x_range[:, np.newaxis]))

    density_distractor = density_target[::-1]
    density_bimodal = (1-p)*density_distractor + p*density_target
    ## the integral is equal to: (1-p) + p = 1
    return density_bimodal

def createBimodalModel_scipy(halfdist, tab, x_range, p, bw="scott"):

    selection_end = (tab.marker == 2) & selectByHalfDistance(tab, halfdist)
    selection_start = (tab.marker == 1) & selectByHalfDistance(tab, halfdist)

    data_driftcorrected = tab.ix[selection_end, ["xp","yp"]].values[:]\
                        - tab.ix[selection_start, ["xp","yp"]].values[:]

    target_dir = tab.ix[selection_end, ["target_dir"]].values[:]
    c = tab.ix[selection_end, ["trial_type"]].values[:]
    c = c.reshape(len(c))

    ## let's just take Y-axis:
    data_mirroted = mirrorConditions(target_dir, data_driftcorrected)[:,1]
    rep_target = int(p*100)
    rep_distractor = 100-rep_target
    bimodal_distr = np.hstack((np.repeat(data_mirroted[c==1], rep_target), np.repeat(-data_mirroted[c==1], rep_distractor)))
    kde = sc.gaussian_kde(bimodal_distr, bw_method = bw) ## condition control
    density_bimodal = kde(x_range)

    return density_bimodal


def giveDensityCurves2(halfdist, tab, x_range):

    selection_end = (tab.marker == 2) & selectByHalfDistance(tab, halfdist)
    selection_start = (tab.marker == 1) & selectByHalfDistance(tab, halfdist)

    data_driftcorrected = tab.ix[selection_end, ["xp","yp"]].values[:]\
                        - tab.ix[selection_start, ["xp","yp"]].values[:]

    target_dir = tab.ix[selection_end, ["target_dir"]].values[:]
    ## let's just take Y-axis:
    data_mirroted = mirrorConditions(target_dir, data_driftcorrected)[:,1]

    c = tab.ix[selection_end, ["trial_type"]].values[:]
    c = c.reshape(len(c))

    model_unimodal = data_mirroted[c==1]
    grid = GridSearchCV( sk.KernelDensity(),{'bandwidth': np.linspace(1.0, 200.0, 30)},cv=20 )
    grid.fit(model_unimodal[:, np.newaxis])
    kde = grid.best_estimator_ ## condition control
    density_unimodal = np.exp(kde.score_samples(x_range[:, np.newaxis]))

    model_bimodal = np.hstack((data_mirroted[c==1], - data_mirroted[c==1]) )
    grid = GridSearchCV( sk.KernelDensity(),{'bandwidth': np.linspace(1.0, 200.0, 30)},cv=20 )
    grid.fit(model_bimodal[:, np.newaxis])
    kde = grid.best_estimator_ ## condition control
    density_bimodal = np.exp(kde.score_samples(x_range[:, np.newaxis]))

    real_data = data_mirroted[c==0]
    grid = GridSearchCV( sk.KernelDensity(),{'bandwidth': np.linspace(1.0, 200.0, 30)},cv=20 )
    grid.fit(real_data[:, np.newaxis])
    kde = grid.best_estimator_ ## condition control
    density_real_data = np.exp(kde.score_samples(x_range[:, np.newaxis]))

    return density_real_data, density_unimodal, density_bimodal, model_bimodal, data_mirroted[c==1].mean()


def giveDensityCurves(halfdist, tab, x_range):

    selection_end = (tab.marker == 2) & selectByHalfDistance(tab, halfdist)
    selection_start = (tab.marker == 1) & selectByHalfDistance(tab, halfdist)

    data_driftcorrected = tab.ix[selection_end, ["xp","yp"]].values[:]\
                        - tab.ix[selection_start, ["xp","yp"]].values[:]

    target_dir = tab.ix[selection_end, ["target_dir"]].values[:]
    ## let's just take Y-axis:
    data_mirroted = mirrorConditions(target_dir, data_driftcorrected)[:,1]

    c = tab.ix[selection_end, ["trial_type"]].values[:]
    c = c.reshape(len(c))

    kde = sc.gaussian_kde(data_mirroted[c==1]) ## condition control
    density_onestim = kde(x_range)
    kde = sc.gaussian_kde(data_mirroted[c==0])
    density_doublestim = kde(x_range)

    return density_onestim, density_doublestim, data_mirroted[c==1].mean(), data_mirroted[c==1].std()


