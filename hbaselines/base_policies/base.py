"""Script containing the abstract policy class."""
import numpy as np
import tensorflow as tf


class Policy(object):
    """Base Policy object.

    Attributes
    ----------
    sess : tf.compat.v1.Session
        the current TensorFlow session
    ob_space : gym.spaces.*
        the observation space of the environment
    ac_space : gym.spaces.*
        the action space of the environment
    co_space : gym.spaces.*
        the context space of the environment
    verbose : int
        the verbosity level: 0 none, 1 training information, 2 tensorflow debug
    layer_norm : bool
        enable layer normalisation
    layers : list of int or None
        the size of the Neural network for the policy
    act_fun : tf.nn.*
        the activation function to use in the neural network
    use_huber : bool
        specifies whether to use the huber distance function as the loss for
        the critic. If set to False, the mean-squared error metric is used
        instead
    """

    def __init__(self,
                 sess,
                 ob_space,
                 ac_space,
                 co_space,
                 verbose,
                 layer_norm,
                 layers,
                 act_fun,
                 use_huber):
        """Instantiate the base policy object.

        Parameters
        ----------
        sess : tf.compat.v1.Session
            the current TensorFlow session
        ob_space : gym.spaces.*
            the observation space of the environment
        ac_space : gym.spaces.*
            the action space of the environment
        co_space : gym.spaces.*
            the context space of the environment
        verbose : int
            the verbosity level: 0 none, 1 training information, 2 tensorflow
            debug
        layer_norm : bool
            enable layer normalisation
        layers : list of int or None
            the size of the Neural network for the policy
        act_fun : tf.nn.*
            the activation function to use in the neural network
        use_huber : bool
            specifies whether to use the huber distance function as the loss
            for the critic. If set to False, the mean-squared error metric is
            used instead
        """
        self.sess = sess
        self.ob_space = ob_space
        self.ac_space = ac_space
        self.co_space = co_space
        self.verbose = verbose
        self.layers = layers
        self.layer_norm = layer_norm
        self.act_fun = act_fun
        self.use_huber = use_huber

    def initialize(self):
        """Initialize the policy.

        This is used at the beginning of training by the algorithm, after the
        model parameters have been initialized.
        """
        raise NotImplementedError

    def update(self, update_actor=True, **kwargs):
        """Perform a gradient update step.

        Parameters
        ----------
        update_actor : bool
            specifies whether to update the actor policy. The critic policy is
            still updated if this value is set to False.
        """
        raise NotImplementedError

    def get_action(self, obs, context, apply_noise, random_actions, env_num=0):
        """Call the actor methods to compute policy actions.

        Parameters
        ----------
        obs : array_like
            the observation
        context : array_like or None
            the contextual term. Set to None if no context is provided by the
            environment.
        apply_noise : bool
            whether to add Gaussian noise to the output of the actor. Defaults
            to False
        random_actions : bool
            if set to True, actions are sampled randomly from the action space
            instead of being computed by the policy. This is used for
            exploration purposes.
        env_num : int
            the environment number. Used to handle situations when multiple
            parallel environments are being used.

        Returns
        -------
        array_like
            computed action by the policy
        """
        raise NotImplementedError

    def get_td_map(self):
        """Return dict map for the summary (to be run in the algorithm)."""
        raise NotImplementedError

    @staticmethod
    def _get_obs(obs, context, axis=0):
        """Return the processed observation.

        If the contextual term is not None, this will look as follows:

                                    -----------------
                    processed_obs = | obs | context |
                                    -----------------

        Otherwise, this method simply returns the observation.

        Parameters
        ----------
        obs : array_like
            the original observation
        context : array_like or None
            the contextual term. Set to None if no context is provided by the
            environment.
        axis : int
            the axis to concatenate the observations and contextual terms by

        Returns
        -------
        array_like
            the processed observation
        """
        if context is not None:
            context = context.flatten() if axis == 0 else context
            obs = np.concatenate((obs, context), axis=axis)
        return obs

    @staticmethod
    def _get_ob_dim(ob_space, co_space):
        """Return the processed observation dimension.

        If the context space is not None, it is included in the computation of
        this term.

        Parameters
        ----------
        ob_space : gym.spaces.*
            the observation space of the environment
        co_space : gym.spaces.*
            the context space of the environment

        Returns
        -------
        tuple
            the true observation dimension
        """
        ob_dim = ob_space.shape
        if co_space is not None:
            ob_dim = tuple(map(sum, zip(ob_dim, co_space.shape)))
        return ob_dim