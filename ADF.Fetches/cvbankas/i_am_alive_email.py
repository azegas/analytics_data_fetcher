from other_stuff.send_email import send_i_am_alive_email


def main():

    send_i_am_alive_email(
        "analytics_data_fetcher",
        "I am alive!",
    )


if __name__ == "__main__":
    main()
