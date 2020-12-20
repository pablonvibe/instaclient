from instaclient.client import *
from instaclient.client.component import Component


class Interactions(Component):

    # FOLLOW PROCEDURE
    @Component._manage_driver()
    def follow_user(self, user:str, nav_to_user:bool=True, _discard_driver:bool=False):
        """
        follow_user follows the instagram user that matches the username in the `user` attribute.
        If the target account is private, a follow request will be sent to such user and a `PrivateAccountError` will be raised.

        Args:
            user (str): Username of the user to follow.
            _discard_driver (bool, optional): If set to True, the driver will be discarded at the end of the method. Defaults to False.

        Raises:
            PrivateAccountError: Raised if the `user` is a private account - A request to follow the user will be sent eitherway.
            InvalidUserError: Raised if the `user` is invalid
        """
        # Navigate to User Page
        if nav_to_user:
            self.nav_user(user, check_user=False)
        
        # Check User Vadility
        try:
            result = self.is_valid_user(user, nav_to_user=False)
            LOGGER.debug('INSTACLIENT: User <{}> is valid'.format(user))
            private = False
            
        # User is private
        except PrivateAccountError:
            private = True

        if self._check_existence(EC.presence_of_element_located((By.XPATH, Paths.REQUESTED_BTN))):
            # Follow request already sent
            pass
        elif self._check_existence(EC.presence_of_element_located((By.XPATH, Paths.MESSAGE_USER_BTN))):
            # User already followed
            pass
        else:
            follow_button = self._find_element(EC.presence_of_element_located((By.XPATH, Paths.FOLLOW_BTN)), url=ClientUrls.NAV_USER.format(user))
            self._press_button(follow_button)

        if private:
            raise FollowRequestSentError(user)

    
    @Component._manage_driver()
    def unfollow_user(self, user:str, nav_to_user=True, check_user=True, _discard_driver:bool=False):
        """
        Unfollows a given user.

        Args:
            user (str): User to unfollow
            nav_to_user (bool, optional): Navigate to user profile page. Defaults to True.
            check_user (bool, optional): Check user vadility. Defaults to True.
            _discard_driver (bool, optional): Discard driver when completed. Defaults to False.

        Raises:
            InvalidUserError: raised if the user specified by the `user` argument is invalid.
        """
        if nav_to_user:
            self.nav_user(user, check_user)
        elif check_user:
            try:
                self.is_valid_user(user, nav_to_user=False)
            except PrivateAccountError:
                pass
            LOGGER.debug('INSTACLIENT: User <{}> is valid'.format(user))

        if self._check_existence(EC.presence_of_element_located((By.XPATH, Paths.UNFOLLOW_BTN))):
            unfollow_btn = self._find_element(EC.presence_of_element_located((By.XPATH, Paths.UNFOLLOW_BTN)))
            self._press_button(unfollow_btn)
            time.sleep(1)
            confirm_unfollow = self._find_element(EC.presence_of_element_located((By.XPATH, Paths.CONFIRM_UNFOLLOW_BTN)))
            self._press_button(confirm_unfollow)
            LOGGER.debug('INSTACLIENT: Unfollowed user <{}>'.format(user))
        elif self._check_existence(EC.presence_of_element_located((By.XPATH, Paths.REQUESTED_BTN))):
            requested_btn = self._find_element(EC.presence_of_element_located((By.XPATH, Paths.REQUESTED_BTN)))
            self._press_button(requested_btn)
            LOGGER.debug(f'Cancelled Follow Request for user <{user}>')

    
    @Component._manage_driver()
    def like_latest_posts(self, user:str, n_posts:int, like:bool=True, _discard_driver:bool=False):
        """
        Likes a number of a users latest posts, specified by n_posts.

        Args:
            user:str: User whose posts to like or unlike
            n_posts:int: Number of most recent posts to like or unlike
            like:bool: If True, likes recent posts, else if False, unlikes recent posts

        TODO: Currently maxes out around 15.
        TODO: Adapt this def
        """

        action = 'Like' if like else 'Unlike'

        self.nav_user(user)

        imgs = []
        elements = self._find_element(EC.presence_of_all_elements_located((By.CLASS_NAME, '_9AhH0')))
        imgs.extend(elements)

        for img in imgs[:n_posts]:
            img.click() 
            time.sleep(1) 
            try:
                self.driver.find_element_by_xpath("//*[@aria-label='{}']".format(action)).click()
            except Exception as e:
                LOGGER.error(e)

            self.driver.find_elements_by_class_name('ckWGn')[0].click()


    @Component._manage_driver()
    def send_dm(self, user:str, message:str, _discard_driver:bool=False):
        """
        Send an Instagram Direct Message to a user. 

        Args:
            user (str): Instagram username of the account to send the DM to
            message (str): Message to send to the user via DMs
            _discard_driver (bool): Discard driver when operation is done.

        Raises:
            InvalidUserError: if the user is invalid.
        """
        # Navigate to User's dm page
        try:
            self.nav_user_dm(user)
            text_area = self._find_element(EC.presence_of_element_located((By.XPATH, Paths.DM_TEXT_AREA)))
            text_area.send_keys(message)
            time.sleep(1)
            send_btn = self._find_element(EC.presence_of_element_located((By.XPATH, Paths.SEND_DM_BTN)))
            self._press_button(send_btn)
            time.sleep(1)
        except Exception as error: 
            if self.debug:
                self.error_callback(self.driver)
            LOGGER.error('INSTACLIENT: An error occured when sending a DM to the user <{}>'.format(user))
            raise error


    # ENGAGEMENT PROCEDURES
    @Component._manage_driver()
    def scroll(self, mode=PAGE_DOWN_SCROLL, size=500, times=1, interval=3):
        """
        Scrolls to the bottom of a users page to load all of their media

        Returns:
            bool: True if the bottom of the page has been reached, else false

        """
        for n in range(0, times):
            self._dismiss_dialogue(wait_time=1)
            LOGGER.debug('INSTACLIENT: Scrolling')
            if mode == self.PIXEL_SCROLL:
                self.driver.execute_script("window.scrollBy(0, {});".format(size))
            elif mode == self.PAGE_DOWN_SCROLL:
                url = self.driver.current_url
                body = self._find_element(EC.presence_of_element_located((By.TAG_NAME, 'body')), retry=True, url=url)
                body.send_keys(Keys.PAGE_DOWN)
            elif mode == self.END_PAGE_SCROLL:
                url = self.driver.current_url
                body = self._find_element(EC.presence_of_element_located((By.TAG_NAME, 'body')), retry=True, url=url)
                body.send_keys(Keys.END)

            time.sleep(interval)
        return False


    @Component._manage_driver()
    def like_feed_posts(self, count):
        LOGGER.debug('INSTACLIENT: like_feed_posts')


