registry.module('forms.user') unless registry.has('forms.user')

showSuccessDialog = (msg) ->
  $.notify(msg)

showWarningDialog = (msg) ->
  $.notify(msg, 'warn')

showFailureDialog = (msg) ->
  $.notify(msg, "error")

(registry.forms.user = (($) ->
  editables = $("input.editable")

  # End of Authenticator Class
  originals = {}
  changes = []
  auth = null

  getUniqueId = (elem) ->
    return elem.hnExtensions.uniqueId if elem.hnExtensions?.uniqueId?

    if not elem.hnExtensions?
      elem['hnExtensions'] = {}

    return elem.hnExtensions['uniqueId'] = _.uniqueId('hn_change_uid')


  editables.prop('readonly', true).addClass('no-input').each(->
    originals[getUniqueId(@)] = $(@).val()
  )

  createReversion = ->
    (elem, old) -> $(elem).val(old)

  revertChanges = ->
    c.revert() for c in changes
    changes = []

  handleFailedChanges = (changes) ->
    console.dir(changes)
    c.revert() for c in changes[0]
    return

  handleConfirmedChanges = (changes) ->
    console.dir(changes)
    originals[getUniqueId($(c.target))] = c.new for c in changes[0]
    return

  commitChanges = ->
    console.dir(changes)
    return if changes.length == 0
    vex.dialog.buttons.YES.text = 'Confirm'
    vex.dialog.buttons.NO.text = 'Cancel'
    vex.dialog.confirm
      message: "Do you want to submit the current changes to the user profiles?"
      callback: (value) ->
        if not value then revertChanges()
        else
          auth.commitChanges(changes, (err, confirmed, failed) ->
            handleConfirmedChanges(confirmed)
            handleFailedChanges(failed)
            changes = []

            unless err
              return registry.postNotification(registry.getVisitorUuid(), null, "Successfully updated profile!", "success", ->
                location.reload(yes))
            showFailureDialog("Failed to update profile!: #{err.message}")
          )


  hookPermissions = (uuid) ->
    throw new Error('Cannot reassign editability!') if auth?

    auth = new Authenticator(uuid)

    applyReadonlyUnlessFocused = (editables, filterword, perm) ->
      editables.filter(-> $(@).data('auth-type') is filterword)
      .click(-> $(@).prop('readonly', false))
      .blur(-> $(@).prop('readonly', true))
      .change(->
        console.dir("CHANGED: #{$(@)}")
        if $(@).val() != originals[getUniqueId(@)]
          changes.push(new Change(@, $(@).val(), originals[getUniqueId(@)], createReversion(), perm))
      )
      .removeClass('no-input')

    auth.use((error, perms) ->
      for p in perms
        switch p
          when 'edit.personal'
            applyReadonlyUnlessFocused(editables, 'personal', 'edit.personal')
          when 'edit.medical'
            applyReadonlyUnlessFocused(editables, 'medical', 'edit.medical')
          when 'edit.insurance'
            applyReadonlyUnlessFocused(editables, 'insurance', 'edit.insurance')

      return
    )

  return {
    hook: hookPermissions
    isAuthUser: (uuid) -> if auth? then auth.checkUser(uuid) else no
    updateUser: commitChanges,
    getOwnerUuid: -> if auth? then auth.uuid else null
  })(jQuery))

(($, _) -> $(document).ready(->
  tabLinks = $("#tab-links")
  tabLinkListItems = tabLinks.find('li')
  innerTabLinks = $("#innertab-links")
  innerTabLinksListItems = innerTabLinks.find('li')

  # Top Level Tab Click Handling
  tabLinkListItems.click((event) ->
# Store reference to self and active and disable current active tab
    jSelf = $(@)
    active = tabLinkListItems.find('.active')
    active.removeClass('active')

    # Set self to active, hide tab content and fade in the tab
    # owned by self
    jSelf.addClass('active')
    $('.tab').hide()
    $(jSelf.find('a').attr('href')).fadeIn()

    # Prevent redirection to link
    registry.stopEventBehavior(event)
  )

  # Extremely similar to above
  innerTabLinksListItems.click((event) ->
    jSelf = $(@)
    active = innerTabLinksListItems.find('.active')

    active.removeClass('active')
    jSelf.addClass('active')

    $('.tab').hide()
    $(jSelf.find('a').attr('href')).fadeIn()

    registry.stopEventBehavior(event)
  )

  inbox = $("#inbox")
  checkAllBox = $("#checkAll")
  msgSender = $("#message_sender")
  msgDate = $("#message_date")
  msgTitle = $("#message_title")
  msgContent = $("#message_content")
  msgCreateForm = $("#msg-create-form-html")

  checkAllBox.change(-> $("input#msg-checkbox").prop('checked', $(@).prop('checked')))
  checkAllBox.on('msg:uncheck', -> checkAllBox.click() if checkAllBox.is(':checked'))

  uncheckHandler = -> checkAllBox.trigger('msg:uncheck') unless $(@).is(':checked')
  messageOpenHandler = ->
    jSelf = $(@)
    parentRow = jSelf.parent('tr')
    selected = parentRow.attr('href')
    uuid = parentRow.data('message-id')

    $.ajax
      url: "msg/#{uuid}"
      type: 'GET'
      success: (resp) ->
        sender = resp.sender['name']
        date = moment(resp['date']).format('MMMM Do YYYY [at] h:mm:ss a')
        title = resp['title']
        content = registry.escapeHtml(resp['content']).replace(/(?:\r\n|\r|\n)/g, '<br />')

        msgSender.text(sender)
        msgDate.text(date)
        msgTitle.text(title)
        msgContent.html(content)

        $(".tab").hide()
        $(selected).fadeIn()

  $('input#msg-checkbox').change(uncheckHandler)

  inbox.find("td").not('.check-box-wrapper').click(messageOpenHandler)

  $("#newMessage").click((event) ->
    form = msgCreateForm.clone()
    document.getElementById('msgCreation').reset()

    form.css("display", "block")
    form.find('span.help-inline').remove()

    vex.dialog.buttons.YES.text = 'Send'
    vex.dialog.open
      message: form
      callback: (data) ->
        return unless data

        vexContent = $('.vex-content')
        title = vexContent.find('#id_title').val()
        receiver = vexContent.find('#id_receiver').find(':selected').val()
        console.log(vexContent.find('#id_content').val())
        $.ajax
          url: '/msg'
          type: 'POST'
          data:
            receiver: registry.escapeHtml(receiver)
            content: vexContent.find('#id_content').val() || ''
            title: registry.escapeHtml(title)
          success: (resp) ->
            return unless resp.success && registry.forms.user.isAuthUser(receiver)

            tmpId = 'TEMP-MESSAGE-ID-FOR-CLICK'
            time = moment(resp.timestamp).format('MMMM D, YYYY, h:mm a').replace(`/ am/g`, ' a.m.').replace(`/ pm/g`, ' p.m.')
            inbox.find('tbody').prepend("""
                  <tr data-message-id="#{resp.id}" class="inbox-row" href="#tab7" id="#{tmpId}">
                     <td class="inboxBody check-box-wrapper">
                        <input id="msg-checkbox" type="checkbox"/>
                     </td>
                     <td class="inboxBody">#{resp.sender}</td>
                     <td id="title" class="inboxBody"></td>
                     <td class="inboxBody">#{time}</td>
                  </tr>
                  """)
            tmp = $("##{tmpId}")
            tmp.find('td#title').text(title)
            tmp.find('td').not('.check-box-wrapper').click(messageOpenHandler)
            tmp.attr('id', null)
            vex.close()
  )

  $("#id-delete-msg").click(->
    mIds = []
    inbox.find('input:checked').not('#checkAll').each(-> mIds.push $(@).parent('td').parent('tr').data('message-id'))
    return unless mIds.length > 0

    msgHandler = (messages, failures) ->
      messages = _.without(messages, failures)
      _.each(messages, (mId) -> $(".inbox-row[data-message-id='#{mId}'").remove())
      checkAllBox.trigger('msg:uncheck')

    $.ajax
      url: 'msg/' + mIds[0]
      type: 'DELETE'
      data:
        messages: mIds
      success: (resp) -> msgHandler(mIds, resp.fails)
  )

  $("#Dismiss").click(->
    $('#sysMessage')[0].style.display = 'none'
  )

  $('#patientSearchBar').keyup ->
    searchTable $(this).val()
    return

  searchTable = (inputVal) ->
    table = $('#patient')
    table.find('tr').each (index, row) ->
      allCells = $(row).find('td')
      if allCells.length > 0
        found = false
        allCells.each (index, td) ->
          regExp = new RegExp(inputVal, 'i')
          if regExp.test($(td).text())
            found = true
            return false
          return
        if found == true
          $(row).show()
        else
          $(row).hide()
      return
    return

  # TODO This may be re-worked, the constant fade is annoying
  buttonButtonsPresButtonsHandler = (evt) ->
    console.log('PresButtonsHandler')
    $('.tab').hide()
    $($(@).find('a').attr('href')).fadeIn()
    registry.stopEventBehavior(evt)

  $('#buttons').click(buttonButtonsPresButtonsHandler)
  $('#presbuttons').click(buttonButtonsPresButtonsHandler)
  $('#button').click(buttonButtonsPresButtonsHandler)

  $('#release-test-btn').click(->
    self = $(@)
    id = self.data('test-id')

    $.ajax(
      url: "/user/#{registry.forms.user.getOwnerUuid()}/test"
      type: 'PUT'
      data:
        "test-id": id
      success: ->
        self.remove()
    )
  )

  $('button.inbox-btn').click((event) ->
    $(".tab").hide()

    selected_tab = $(this).parent('a').attr("href")

    $(selected_tab).fadeIn(20)
    registry.stopEventBehavior(event)
  )

  $('button#discharge-btn').click(->
    self = $(@)
    pname = self.data('patient-name')
    id = self.data('patient-id')

    vex.dialog.buttons.YES.text = 'Confirm'
    vex.dialog.buttons.NO.text = 'Cancel'

    vex.dialog.confirm
      message: "Are you sure you want to discharge #{pname}?"
      callback: (result) ->
        return unless result

        $.ajax
          url: "/patient_discharge/#{id}"
          type: 'POST'
          success: -> location.reload(yes)
  )
))(jQuery, _)