from requests_html import HTMLSession

sess = HTMLSession()
graphql_url = "https://czmclaudiu.medium.com/_/graphql"

payload = {
    "operationName": "UserProfileQuery",
    "query": 
    """query UserProfileQuery($id: ID, $username: ID, $homepagePostsLimit: PaginationLimit, $homepagePostsFrom: String = null, $includeDistributedResponses: Boolean = true, $name: String = null) {
    userResult(id: $id, username: $username, name: $name) {
        __typename
            ... on User {
    id
    name
    viewerIsUser
    viewerEdge {
    id
    isFollowing
    __typename
    }
    homePostsPublished: homepagePostsConnection(paging: {limit: 1}) {
    posts {
    id
    __typename
    }
    ...ion
    ...CollectionAvatar_collection
    ...MetaHeaderTop_collection
    __typename
    id
    }
    ... on User {
    username
    id
    __typename
    }
    }

    fragment MetaHeaderTop_collection on Collection {
    id
    creator {
    id
    __typename
    }
    __typename
    }

    fragment CollectionNavigationContextProvider_collection on Collection {
    id
    domain
    slug
    isAuroraVisible
    __typename
    }

    fragment useShouldShowEntityDrivenSubscription_creator on User {
    id
    __typename
    }""",
    
    
    
    "variables": 
    {
        "homepagePostsFrom": "L1675805671776",
        "homepagePostsLimit": 10,
        "id": "e0901a21f36c",
        "includeDistributedResponses": "true",
        "username": "null"
    }
}

r = sess.post(graphql_url, json=payload)

print(r.status_code)

print(r.text)