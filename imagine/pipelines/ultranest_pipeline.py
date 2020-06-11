import numpy as np
import logging as log
import ultranest
from imagine.pipelines.pipeline import Pipeline
from imagine.tools.icy_decorator import icy


@icy
class UltranestPipeline(Pipeline):
    """
    Initialises Bayesian analysis pipeline with pyMultinest

    See base class for initialization details.

    Note
    ----
    Instances of this class are callable
    """
    @property
    def sampler_supports_mpi(self):
        return True

    def __call__(self, **kwargs):
        """
        Runs the IMAGINE pipeline using the UltraNest sampler
        
        Returns
        -------
        results : dict
            pyMultinest sampling results in a dictionary containing the keys:
            logZ (the log-evidence), logZerror (the error in log-evidence) and
            samples (equal weighted posterior)
        """
        log.debug('@ ultranest_pipeline::__call__')

        # Resets internal state
        self.tidy_up()

        # Runs pyMultinest
        self.sampler = ultranest.ReactiveNestedSampler(
            param_names=list(self.active_parameters),
            loglike=self._likelihood_function,
            transform=self.prior_transform,
            #resume='subfolder',
            #run_num=None,
            #log_dir=None,
            #num_test_samples=2,
            #draw_multiple=True,
            #num_bootstraps=30,
            vectorized=False)

        kwargs_actual = {'viz_callback': False}
        kwargs_actual.update(self.sampling_controllers)
        kwargs_actual.update(kwargs)

        self.results = self.sampler.run(**kwargs_actual)

        self._samples_array = self.results['samples']
        self._evidence = self.results['logz']
        self._evidence_err = self.results['logzerr']

        return self.results
