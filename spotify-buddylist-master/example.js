const buddyList = require('./')

async function main () {
  const spDcCookie = 'AQDwNzNoi5kSpdy6M176vl183KcxelaVHcLkvr8FbUjtPXlU9mtv8DVlCrgCKWXgGyZmNGpj--ZRySlS9L0MMayf6Zo7UwCtXqLnxm5jMKpjp3E7YeEUDXr5FRCbQTjBRaXQYEOHzq6-wUwDM2dasxlFBUvlYkXX'

  const { accessToken } = await buddyList.getWebAccessToken(spDcCookie)
  const friendActivity = await buddyList.getFriendActivity(accessToken)

  console.log(JSON.stringify(friendActivity, null, 2))
}

main()

// Run every minute
// setInterval(() => main(), 1000 * 60)
